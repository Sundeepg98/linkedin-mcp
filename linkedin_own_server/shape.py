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


def split_lines(text: str) -> list[str]:
    """Split text into whitespace-normalised, non-empty lines. No filtering."""
    out: list[str] = []
    for raw in str(text or "").splitlines():
        line = _WS.sub(" ", raw).strip()
        if line:
            out.append(line)
    return out


def drop_consecutive_repeats(lines: Iterable[str]) -> list[str]:
    """Collapse a line that immediately repeats the one before it."""
    out: list[str] = []
    for line in lines:
        if out and out[-1].casefold() == line.casefold():
            continue
        out.append(line)
    return out


def clean_lines(text: str) -> list[str]:
    """Split card text into non-empty lines, dropping LinkedIn's echoes.

    LinkedIn renders many labels twice -- once visually and once in a
    screen-reader-only span -- so raw ``innerText`` is full of consecutive
    duplicates. Collapsing them is not cosmetic: without it the company name
    of a job card is whatever the duplicate of the title happens to be.
    """
    return drop_consecutive_repeats(split_lines(text))


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
    # The call to action on a job-alert notification, which LinkedIn draws
    # twice -- once visible, once for screen readers -- so one copy survives
    # the screen-reader subtraction and lands in the notification body.
    "view jobs",
    "add note",
    # The notification card's overflow menu. LinkedIn keeps these behind a
    # button, so whether they reach innerText depends on whether the menu is
    # open -- the same render-state dependency the harvesters are arranged to
    # be immune to. Named here so the body reads the same either way.
    "change notification preferences",
    "delete notification",
    "show less like this",
}


#: The middle dot LinkedIn uses to separate two facts on one line, spelled
#: this way so the source file stays pure ASCII.
MIDDLE_DOT = chr(0xB7)

#: Punctuation that decorates a chrome label without being part of it.
#: chr(0x2022) is the bullet in front of a connection-degree badge.
_LABEL_PUNCTUATION = " .*-" + MIDDLE_DOT + chr(0x2022)


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


#: A compact time with NO "ago" after it: "22m", "2h", "3d", "2mo".
#:
#: Deliberately NOT folded into :func:`find_time_ago`. That function scans free
#: text, where dropping the "ago" would read "3M Company" as three months and
#: "1 reaction" would only be spared by luck. This one is applied ONLY to a
#: string the page has already declared to be a timestamp -- the notification
#: card's own time element -- so there is nothing for it to misread.
_BARE_COMPACT_TIME = re.compile(r"^(\d+)\s*(mo|s|m|h|d|w|y)$", re.I)


def compact_time_ago(text: Optional[str]) -> Optional[str]:
    """``'2h'`` -> ``'2 hours ago'``. Only for a known timestamp carrier."""
    match = _BARE_COMPACT_TIME.match(str(text or "").strip())
    if not match:
        return None
    return _spell(match.group(1), _COMPACT_UNITS[match.group(2).lower()])


def split_on_middle_dot(line: str) -> Optional[tuple[str, str]]:
    """Split ``'Acme Corp <dot> Berlin (Remote)'`` into its two halves.

    Returns ``None`` unless the line splits into EXACTLY two non-empty parts,
    so a line carrying two separators -- or none -- is left alone rather than
    guessed at.
    """
    parts = [part.strip() for part in str(line or "").split(MIDDLE_DOT)]
    parts = [part for part in parts if part]
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


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

    On the job tracker the second and third are ONE line -- "Ashgrove Systems
    <dot> Fairhaven (Remote)" -- so the company slot is split on the separator
    when, and only when, it yields exactly two parts. Without that the location
    is whatever line happened to come next, which on a tracker row is the
    column header "Notes".
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

    title = remaining[0]
    rest = remaining[1:]
    if rest:
        halves = split_on_middle_dot(rest[0])
        if halves:
            rest = [halves[0], halves[1]] + rest[1:]

    job_id = job_id_from(record.get("href", ""))
    out: dict[str, Any] = {
        "title": trim(title, 120),
        "company": trim(rest[0], 100) if rest else None,
        "location": trim(rest[1], 100) if len(rest) > 1 else None,
    }
    if status:
        out["status"] = status
    if when:
        out["when"] = when
    if job_id:
        out["job_id"] = job_id
        out["url"] = f"https://www.linkedin.com/jobs/view/{job_id}"
    return out


def strip_screen_reader_copies(
    text: str, hidden: Iterable[str], *, also: Iterable[str] = ()
) -> list[str]:
    """Remove the screen-reader duplicates from a card's text, exactly.

    ``innerText`` includes visually-hidden text, so a notification body arrives
    with "Unread notification." and "Status is reachable" welded onto it. The
    obvious fix -- a list of a11y phrases to delete -- is wrong twice over: it
    is always one LinkedIn wording behind, and some hidden strings are a second
    copy of the VISIBLE body, so deleting by phrase empties the notification.

    So the subtraction is by COUNT, not by phrase: each hidden element removes
    ONE occurrence of its own text. A string the page marked hidden once and
    printed once vanishes; a string it marked hidden once and printed twice
    keeps its visible copy. Nothing here needs to know what any of them say.

    The subtraction runs twice, and the second pass is not decoration. Whether
    a hidden copy lands on its OWN innerText line or welded onto the visible
    one is a question of LAYOUT, and layout is exactly the kind of state that
    differs between one render and the next. The first pass removes whole
    lines; the second removes what is left as a substring, longest string
    first so a long hidden body is taken out before a short label that might
    sit inside it. Either way each hidden element accounts for exactly one
    occurrence, so the same page reads the same both ways round.
    """
    budget: dict[str, int] = {}
    for item in list(hidden or ()) + list(also or ()):
        for line in split_lines(item):
            budget[line] = budget.get(line, 0) + 1

    kept: list[str] = []
    for line in split_lines(text):
        if budget.get(line):
            budget[line] -= 1
            continue
        kept.append(line)

    for needle in sorted(budget, key=len, reverse=True):
        while budget[needle] > 0:
            for index, line in enumerate(kept):
                position = line.find(needle)
                if position < 0:
                    continue
                merged = (
                    line[:position] + " " + line[position + len(needle) :]
                ).strip()
                merged = _WS.sub(" ", merged)
                if merged:
                    kept[index] = merged
                else:
                    kept.pop(index)
                break
            else:
                break
            budget[needle] -= 1
    return kept


def parse_notification(record: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Shape one notification row into a single line of text plus a link.

    ``when`` comes from the card's own timestamp element when the harvest found
    one. It has to: LinkedIn writes "2h" there and nowhere else, with no "ago"
    anywhere on the card, so scanning the body for a time found nothing on all
    22 rows of a real page.
    """
    stamp = str(record.get("time") or "").strip()
    lines = drop_consecutive_repeats(
        strip_screen_reader_copies(
            record.get("text", ""),
            record.get("hidden") or (),
            # The timestamp is printed in the body too. It is not hidden text,
            # but it is the same kind of duplicate: reported as a field, so it
            # should not also be a dangling "22m" on the end of the sentence.
            also=[stamp] if stamp else (),
        )
    )
    lines = [line for line in lines if not is_chrome(line)]
    if not lines:
        return None
    when = compact_time_ago(stamp) or find_time_ago(lines)
    # Drop lines that ARE the timestamp; keep lines that merely contain one,
    # or a notification reading "viewed your profile today" loses its text.
    body = " ".join(ln for ln in lines if not is_timestamp_line(ln))
    body = trim(body)
    if not body:
        return None
    out: dict[str, Any] = {"text": body}
    if when:
        out["when"] = when
    if record.get("unread") is not None:
        # The one fact reading the page destroys, so it is reported as of the
        # moment it was read. See the tool docstring on the cleared badge.
        out["unread"] = bool(record["unread"])
    link = absolute_url(record.get("href", ""))
    if link:
        out["link"] = link
    return out


# ---------------------------------------------------------------------------
# The job tracker's own furniture
# ---------------------------------------------------------------------------

#: A tab in the tracker's strip: "Saved <dot> 0", "In Progress <dot> 1".
#: The count is the whole reason this is parsed. LinkedIn's tabs are
#: client-side radios rather than links, so the count beside the label is the
#: only number on the page that says how long the list SHOULD be -- and it is
#: what makes a genuinely empty list distinguishable from a failed read.
_TRACKER_TAB = re.compile(
    r"^(saved|applied|interview|archived|in progress|draft|clicked apply)"
    r"\s*" + re.escape(MIDDLE_DOT) + r"\s*([\d,]+)$",
    re.I,
)

#: What LinkedIn prints where the rows would be when there are none. Two
#: wordings, measured: the default Saved tab says the first, a tab reached
#: through ``?stage=`` says the second.
TRACKER_EMPTY_MARKERS = ("No jobs here", "No matches")


def parse_tracker_tabs(main_text: str) -> dict[str, int]:
    """Read the tracker's tab strip into ``{'saved': 0, 'applied': 0, ...}``.

    Keys are normalised to lower snake case, so "In Progress" becomes
    ``in_progress``. A tab with no count -- Archived is drawn without one --
    is simply absent rather than reported as zero.
    """
    counts: dict[str, int] = {}
    for line in split_lines(main_text):
        match = _TRACKER_TAB.match(line)
        if not match:
            continue
        key = match.group(1).strip().lower().replace(" ", "_")
        try:
            counts[key] = int(match.group(2).replace(",", ""))
        except ValueError:  # pragma: no cover - the pattern already forbids it
            continue
    return counts


def tracker_empty_state(main_text: str) -> Optional[str]:
    """Return the empty-state wording the page showed, if it showed one."""
    lines = split_lines(main_text)
    for marker in TRACKER_EMPTY_MARKERS:
        for line in lines:
            if line.casefold() == marker.casefold():
                return marker
    return None


def empty_is_believable(
    *, linkedin_count: Optional[int], empty_state: Optional[str]
) -> bool:
    """Is a zero-row harvest an EMPTY LIST, or a READ THAT FAILED?

    The two are indistinguishable from the rows alone -- both are ``[]`` -- and
    conflating them is how a broken parser reports "you have applied to
    nothing" to somebody who has applied to forty things. So a zero is only
    believed when the page itself corroborates it: LinkedIn's own tab count
    says zero, AND the page drew its empty state. Anything else is a failure
    and is reported as one.
    """
    return linkedin_count == 0 and bool(empty_state)


# ---------------------------------------------------------------------------
# The operator's own profile
# ---------------------------------------------------------------------------

#: A pronoun line, which LinkedIn draws directly under the name -- exactly
#: where the headline would otherwise be, so it wins the headline unless it is
#: recognised.
_PRONOUNS = re.compile(r"^[a-z]{2,6}\s*/\s*[a-z]{2,6}$", re.I)

#: "268 connections", "500+ followers". A relationship count, never a location.
_COUNT_LINE = re.compile(r"^[\d,]+\+?\s+(connections?|followers?)$", re.I)

#: Topcard furniture: buttons and prompts LinkedIn packs in beside the name.
_TOPCARD_CHROME = frozenset(
    {
        "contact info",
        "add section",
        "add custom button",
        "enhance profile",
        "open to",
        "resources",
        "show details",
        "add services",
        "get started",
        "edit",
        "more",
    }
)

#: Section headings LinkedIn uses on a profile. Used only to separate the
#: profile's own sections from page furniture ("Analytics", "Ad Options") when
#: reporting what rendered -- never to decide whether a section exists.
PROFILE_SECTION_HEADINGS = (
    "About",
    "Experience",
    "Education",
    "Skills",
    "Licenses & certifications",
    "Projects",
    "Courses",
    "Honors & awards",
    "Languages",
    "Volunteering",
    "Recommendations",
    "Publications",
    "Patents",
    "Organizations",
    "Test scores",
    "Featured",
    "Activity",
    "Interests",
)


def _is_topcard_chrome(line: str) -> bool:
    stripped = line.casefold().strip(_LABEL_PUNCTUATION)
    return not stripped or stripped in _TOPCARD_CHROME or is_chrome(line)


def parse_profile_topcard(lines: Iterable[str]) -> dict[str, Any]:
    """Read name, headline and location out of the topcard's own lines.

    The order LinkedIn draws them in is name, pronouns (optional), headline,
    location -- then a separator, "Contact info", the school, and a connection
    count. Everything that is not one of the three wanted fields is skipped by
    what it IS (a pronoun pair, a count, a button label), never by its
    position, because the pronoun line is optional and a positional rule would
    hand the headline to whoever has pronouns showing.

    Measured on both the pre-hydration and hydrated renders of the same page:
    the lines are identical, which is why this needs no hydration branch.

    The location is taken as the LAST eligible line before "Contact info"
    rather than as the second eligible line overall. LinkedIn always draws the
    location immediately above that link, and anchoring there survives extra
    lines appearing between the headline and the location -- the school name
    does exactly that on some renders, and reading positionally handed it back
    as the location.
    """
    ordered = [line for line in lines if line]
    out: dict[str, Any] = {"name": None, "headline": None, "location": None}
    if not ordered:
        return out

    out["name"] = trim(ordered[0], 120)

    eligible = [
        index
        for index, line in enumerate(ordered)
        if index > 0
        and not _PRONOUNS.match(line)
        and not _COUNT_LINE.match(line)
        and not _is_topcard_chrome(line)
    ]
    if not eligible:
        return out

    contact_at = next(
        (
            index
            for index, line in enumerate(ordered)
            if line.casefold().strip(_LABEL_PUNCTUATION) == "contact info"
        ),
        None,
    )
    before_contact = (
        [index for index in eligible if index < contact_at]
        if contact_at is not None
        else []
    )
    # Two or more eligible lines above Contact info means the first is the
    # headline and the last is the location. One means there is a headline and
    # no location, and inventing one out of the headline is the failure this
    # guards.
    if len(before_contact) >= 2:
        out["headline"] = trim(ordered[before_contact[0]], 240)
        out["location"] = trim(ordered[before_contact[-1]], 240)
        return out

    out["headline"] = trim(ordered[eligible[0]], 240)
    if not before_contact and len(eligible) > 1:
        out["location"] = trim(ordered[eligible[1]], 240)
    return out


_TITLE_SUFFIX = re.compile(r"\s*\|\s*LinkedIn\s*$", re.I)


def name_from_title(title: Optional[str]) -> Optional[str]:
    """``'Alex Rivera | LinkedIn'`` -> ``'Alex Rivera'``."""
    cleaned = _TITLE_SUFFIX.sub("", str(title or "")).strip()
    return cleaned or None


def pick_topcard(
    sections: list[dict[str, Any]], title: Optional[str] = ""
) -> Optional[dict[str, Any]]:
    """Return the section that is the profile's topcard.

    The topcard is where the name, headline and location live. It is normally
    the first section on the page, but "first" is a position and positions
    move, so the document title is used as a cross-check: the section whose
    heading IS the profile owner's name is the topcard wherever it sits. The
    first section is the fallback for a page with no usable title.
    """
    wanted = name_from_title(title)
    if wanted:
        for section in sections or ():
            heading = str(section.get("heading", "")).strip()
            if heading.casefold() == wanted.casefold():
                return section
    return sections[0] if sections else None


def profile_section_lines(
    sections: Iterable[dict[str, Any]], heading: str
) -> list[str]:
    """Return one section's lines WITHOUT its heading line."""
    for section in sections or ():
        if str(section.get("heading", "")).strip().casefold() == heading.casefold():
            lines = [str(line) for line in section.get("lines") or []]
            if lines and lines[0].strip().casefold() == heading.casefold():
                lines = lines[1:]
            return lines
    return []


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
