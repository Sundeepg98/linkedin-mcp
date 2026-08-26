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
from urllib.parse import parse_qs, unquote, unquote_plus, urlsplit

from linkedin_server.config import MAX_TEXT_CHARS

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


def lines_after(lines: list[str], value: Optional[str]) -> list[str]:
    """The lines FOLLOWING the first one that is exactly ``value``.

    Finding a field by its own text rather than by its index is what lets the
    NEXT field survive a line inserted above it. When ``value`` is not among
    the lines -- LinkedIn spells a company one way in the logo's alt text and
    another in the card body, say -- the caller gets everything after the
    first line, which is the old positional behaviour and no worse than it.
    """
    if value:
        needle = value.casefold()
        for index, line in enumerate(lines):
            if line.casefold() == needle:
                return lines[index + 1 :]
    return lines[1:]


def anchored_title(record: dict[str, Any]) -> Optional[str]:
    """The title, read off the link that MAKES this row a job row.

    Accepted only when the link's text reduces to exactly ONE line, because
    that is the test for "this link names one thing". On a search card it
    does: LinkedIn draws the title twice inside the anchor, once for sight and
    once for a screen reader, and subtracting the hidden copy leaves the title
    alone. On the job tracker the whole card sits inside a single anchor, so
    its text is several lines, and this returns ``None`` -- the caller falls
    back to reading lines in order, which is what that surface has always
    needed.

    The subtraction is what makes this render-independent. With LinkedIn's
    stylesheet the hidden copy is absolutely positioned and arrives as a line
    of its own; without it the two copies arrive welded into one line.
    :func:`strip_screen_reader_copies` removes exactly one occurrence either
    way, so the answer is the same on both.
    """
    text = record.get("link_text")
    if not text:
        return None
    reduced = [
        line
        for line in strip_screen_reader_copies(text, record.get("link_hidden") or ())
        if not is_chrome(line)
    ]
    if len(reduced) != 1:
        return None
    return reduced[0]


def parse_job_card(record: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Shape one job row (saved, applied, or a search result).

    Each field is ANCHORED on the thing that identifies it, and only falls
    back to "the next line" when the card did not offer the anchor:

    * **title** -- the text of the job link (:func:`anchored_title`).
    * **company** -- ``logo_name``, the accessible name LinkedIn gives the
      employer's logo. An image is not a line.
    * **location** -- ``meta_line``, the first entry of the metadata list
      inside the entity lockup.

    That matters because reading a card as "line 1, line 2, line 3" makes
    every field hostage to whatever LinkedIn inserts above it. A verified
    employer inserts a screen-reader line reading "<title> with verification":
    on 5 of 14 rows measured live on 2026-08-22 it became the ``company`` and
    pushed the real company down into ``location``. "Promoted", "Viewed",
    "Actively reviewing applicants", a salary chip and an alumni line were on
    the same page, and each is capable of the same shift.

    Two subtractions run before any of it. The card's own screen-reader copies
    are removed by COUNT, so a decoration the page declared hidden is gone
    without this module knowing the phrase; and anything matching a status or
    a relative timestamp is lifted out so it cannot be mistaken for a field.

    On the job tracker the company and location are ONE line -- "Ashgrove
    Systems <dot> Fairhaven (Remote)" -- so the company slot is split on the
    separator when, and only when, it yields exactly two parts. Without that
    the location is whatever line happened to come next, which on a tracker
    row is the column header "Notes".
    """
    lines = [
        line
        for line in drop_consecutive_repeats(
            strip_screen_reader_copies(
                record.get("text", ""), record.get("hidden") or ()
            )
        )
        if not is_chrome(line)
    ]
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

    # Matching is done on the FULL value and trimming only on the way out. A
    # title long enough to be cut would otherwise no longer equal the line it
    # came from, and every field after it would silently go positional again.
    title = anchored_title(record) or remaining[0]

    rest = lines_after(remaining, title)
    if rest:
        halves = split_on_middle_dot(rest[0])
        if halves:
            rest = [halves[0], halves[1]] + rest[1:]

    company = record.get("logo_name") or (rest[0] if rest else None)

    location = record.get("meta_line") or None
    if location and location in (title, company):
        # The lockup's first list held something that is already reported. Its
        # order has moved; the lines are the better answer.
        location = None
    if not location:
        tail = lines_after(rest, company)
        location = tail[0] if tail else None

    job_id = job_id_from(record.get("href", ""))
    out: dict[str, Any] = {
        "title": trim(title, 120),
        "company": trim(company, 100),
        "location": trim(location, 100),
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
        # TURN THE URL INTO SOMETHING THE CALLER CAN ACT ON.
        #
        # A bare link is an identifier that no tool on this server accepts:
        # there is nothing here that takes a url. So a caller who wants to do
        # anything with a notification has to parse the link themselves, or
        # make a round trip to find the key. Both of the keys below are
        # already accepted by tools that ship, and both are sitting in the
        # href unread.
        #
        # This ADDS tokens per row, which is the opposite of the size pass,
        # and it is the right trade for the reason that pass named: noise
        # costs context, but a missing field costs a whole ROUND TRIP. A
        # keyword a caller can pass straight to linkedin_search_jobs is worth
        # more than the dozen tokens it occupies.
        out.update(notification_handles(link))
    return out


#: The two keys a notification link can carry that some tool here accepts.
#: Measured against the tracked notifications fixture, whose links are job
#: ALERTS (a saved search), feed posts, member profiles and one company.
#:
#: NOT job postings -- and that is worth writing down, because it is the
#: obvious guess and it is wrong. No notification link in the fixture is a
#: /jobs/view/<id> url, so there is no job_id to extract here and a reader
#: that tried would find nothing and report nothing, which looks identical to
#: a notification that has no job.
_ALERT_KEYWORDS = re.compile(r"[?&]keywords=([^&]+)")
_COMPANY_LINK = re.compile(r"/company/(\d{4,})")


def notification_handles(link: str) -> dict[str, Any]:
    """Keys from a notification url that a tool on this server will take.

    ``search_keywords`` goes to ``linkedin_search_jobs``; ``company_id`` goes
    to ``linkedin_unfollow_company`` and to ``linkedin_followed_companies``'s
    output shape. Absent when the link carries neither, which is most of them
    -- a feed post or a member profile has no key this server can use, and
    saying nothing is the honest answer rather than inventing one.
    """
    out: dict[str, Any] = {}
    if not link:
        return out
    match = _ALERT_KEYWORDS.search(link)
    if match:
        raw = unquote_plus(match.group(1))
        cleaned = _WS.sub(" ", raw).strip()
        if cleaned:
            out["search_keywords"] = trim(cleaned, 120)
    company = _COMPANY_LINK.search(link)
    if company:
        out["company_id"] = company.group(1)
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
# One job posting
# ---------------------------------------------------------------------------
#
# Every list surface in this server returns CARDS, and a card cannot settle a
# decision: it has no pay, no applicant count and no description. Those three
# live only on the posting, which is why this parser exists.
#
# NOTHING BELOW IS READ BY LINE NUMBER. That is not a style preference. The
# job-card parser on this repo was broken for precisely the other reason --
# "line 1, line 2, line 3" made every field hostage to whatever LinkedIn
# inserted above it, and a verified-employer badge shifted the company into
# the location slot on 5 of 14 live rows. So each fact here is claimed by
# WHAT IT IS: an applicant count looks like one, a time-ago looks like one, a
# pay range carries a currency mark, and the two chips are matched against
# LinkedIn's own closed vocabularies.

#: The heading LinkedIn puts above the posting body.
JOB_BODY_HEADING = "About the job"

#: Where the posting stops. Everything from here on is the page's own
#: furniture -- alert controls, premium insight panels, the company card --
#: and none of it is the job. chr(0x2026) is the ellipsis in LinkedIn's
#: "... more" truncation affordance, which both ends the visible body and is
#: itself a control rather than a line of the description.
JOB_BODY_STOPS = (
    chr(0x2026) + " more",
    "show more",
    "set alert for similar jobs",
    "put your best foot forward",
    "insights about this job",
    "see how you compare",
    "insights about the company",
    "about the company",
    "more jobs",
    "similar jobs",
    "people also viewed",
)

#: LinkedIn's closed vocabulary for the workplace chip.
WORKPLACE_TYPES = ("Remote", "Hybrid", "On-site", "Onsite")

#: LinkedIn's closed vocabulary for the employment chip. Matched as whole
#: lines: the description says "Type: Contract" and "Location: Remote" in
#: prose, and neither is the chip. Only the header region above the body
#: heading is scanned, which is what keeps the two apart.
EMPLOYMENT_TYPES = (
    "Full-time",
    "Part-time",
    "Contract",
    "Internship",
    "Temporary",
    "Volunteer",
    "Other",
)

#: The hiring signals LinkedIn prints beside the metadata. Matched as
#: phrases inside a line, because LinkedIn welds two of them onto one line
#: ("Promoted by hirer <dot> Actively reviewing applicants") and the useful
#: half is the second one.
JOB_STATUS_PHRASES = (
    "No longer accepting applications",
    "Actively reviewing applicants",
    "Be an early applicant",
    "Actively recruiting",
)

#: "Over 100 applicants", "47 applicants", "1 applicant".
_APPLICANT_COUNT = re.compile(r"^(over\s+)?[\d,]+\+?\s+applicants?$", re.I)

#: Currency marks LinkedIn prints a pay range with, spelled by codepoint so
#: this file stays pure ASCII exactly as :data:`MIDDLE_DOT` does. In order:
#: dollar, rupee, pound, euro, yen.
_CURRENCY_MARKS = "$" + chr(0x20B9) + chr(0x00A3) + chr(0x20AC) + chr(0x00A5)


def job_title_from_document_title(
    document_title: Optional[str], company: Optional[str]
) -> Optional[str]:
    """Recover the job title from ``<title>``, given the employer.

    LinkedIn writes the document title as
    ``"<job title> | <employer> | LinkedIn"``. Splitting on the separator is
    the obvious move and it is WRONG: a real title on this account's own
    search results is "Backend Engineer | Remote", which contains one. So the
    known parts are removed from the END instead, and whatever is left is the
    title however many separators it holds.

    Returns ``None`` rather than a guess when the employer is unknown or when
    the title does not carry it -- a document title belonging to some other
    page must never become this job's title.
    """
    text = str(document_title or "").strip()
    name = str(company or "").strip()
    if not text or not name:
        return None

    suffix = " | LinkedIn"
    if text.casefold().endswith(suffix.casefold()):
        text = text[: -len(suffix)].strip()

    tail = " | " + name
    if not text.casefold().endswith(tail.casefold()):
        return None
    text = text[: -len(tail)].strip()
    return trim(text, 200) or None


def _classify_meta(parts: Iterable[str]) -> dict[str, Optional[str]]:
    """Assign each half of the metadata line by identity, never by order."""
    out: dict[str, Optional[str]] = {
        "location": None,
        "posted": None,
        "applicants": None,
    }
    for part in parts:
        value = part.strip()
        if not value:
            continue
        if out["applicants"] is None and _APPLICANT_COUNT.match(value):
            out["applicants"] = trim(value, 60)
        elif out["posted"] is None and has_time_ago(value):
            out["posted"] = trim(value, 60)
        elif out["location"] is None:
            out["location"] = trim(value, 120)
    return out


def _split_meta_line(lines: Iterable[str]) -> dict[str, Optional[str]]:
    """Find the metadata line and read it, or report nothing found.

    The line is identified by CONTENT: it separates its facts with the middle
    dot and at least one of those facts is recognisably a time or an
    applicant count. A header line that merely contains a dot is not enough,
    or the status line ("Promoted by hirer <dot> ...") would be read as
    metadata and its halves scattered across location and posted.
    """
    for line in lines:
        if MIDDLE_DOT not in line:
            continue
        parts = [p.strip() for p in line.split(MIDDLE_DOT) if p.strip()]
        if len(parts) < 2:
            continue
        if not any(has_time_ago(p) or _APPLICANT_COUNT.match(p) for p in parts):
            continue
        return _classify_meta(parts)
    return {"location": None, "posted": None, "applicants": None}


def _looks_like_pay(line: str) -> bool:
    """A pay range carries a currency mark and a number. Both, not either."""
    return any(mark in line for mark in _CURRENCY_MARKS) and any(
        character.isdigit() for character in line
    )


def _match_vocabulary(lines: Iterable[str], vocabulary: Iterable[str]) -> Optional[str]:
    """The first line that IS one of ``vocabulary``, compared whole."""
    folded = {word.casefold(): word for word in vocabulary}
    for line in lines:
        hit = folded.get(line.strip().casefold())
        if hit:
            return hit
    return None


def _find_status(lines: Iterable[str]) -> Optional[str]:
    for line in lines:
        for phrase in JOB_STATUS_PHRASES:
            if phrase.casefold() in line.casefold():
                return phrase
    return None


def _body_index(lines: list[str]) -> Optional[int]:
    for index, line in enumerate(lines):
        if line.strip().casefold() == JOB_BODY_HEADING.casefold():
            return index
    return None


def _job_body(lines: list[str], start: int) -> Optional[str]:
    """The posting itself: everything under its heading, until the furniture."""
    body: list[str] = []
    for line in lines[start + 1 :]:
        folded = line.strip().casefold()
        if any(folded.startswith(stop) for stop in JOB_BODY_STOPS):
            break
        body.append(line)
    joined = "\n".join(body).strip()
    return trim(joined, 8000) or None


def parse_job_detail(
    main_text: str,
    *,
    company: Optional[str] = None,
    document_title: Optional[str] = None,
) -> dict[str, Any]:
    """Shape one job posting from the page's rendered text.

    ``company`` and ``document_title`` come from the DOM rather than from this
    text, because the page states both explicitly and inferring them from
    lines would be the guess this module exists to avoid.

    Every field is ``None`` when the page did not carry it. A missing fact
    reads as missing and never promotes the next one into its place.
    """
    lines = [line for line in clean_lines(str(main_text or "")) if not is_chrome(line)]

    body_at = _body_index(lines)
    # Only the region ABOVE the body heading is scanned for the header facts.
    # The description says "Type: Contract" and "Location: Remote" in prose,
    # and without this boundary those sentences would be read as the chips.
    header = lines[:body_at] if body_at is not None else lines

    out: dict[str, Any] = {
        "title": job_title_from_document_title(document_title, company),
        "company": trim(company, 200) if company else None,
    }
    out.update(_split_meta_line(header))
    out["salary"] = next(
        (trim(line, 120) for line in header if _looks_like_pay(line)), None
    )
    out["workplace_type"] = _match_vocabulary(header, WORKPLACE_TYPES)
    out["employment_type"] = _match_vocabulary(header, EMPLOYMENT_TYPES)
    out["status"] = _find_status(header)
    out["description"] = _job_body(lines, body_at) if body_at is not None else None
    return out


def job_detail_is_believable(detail: dict[str, Any]) -> bool:
    """Is this a posting that was READ, or a page that did not render?

    The two are not distinguishable from the field values alone -- an
    unrendered shell produces a dict of ``None`` exactly as a parser failure
    would -- so the caller raises on a false here rather than handing back a
    posting with nothing in it. A title with no body, and a body with no
    title, are both failures: LinkedIn sets the document title server-side, so
    the title survives on a page that never drew the job.
    """
    return bool(detail.get("title")) and bool(detail.get("description"))


# ---------------------------------------------------------------------------
# Follow state
# ---------------------------------------------------------------------------

#: The accessible name of the job-posting follow control in each state, and
#: what each one MEANS. Measured 2026-08-23; see ``dom.FOLLOW_CONTROL`` for
#: how, and for why the class attribute carries nothing.
FOLLOW_LABELS: dict[str, str] = {
    "Follow": "not_following",
    "Following": "following",
}

#: Returned instead of a guess. Kept as a named constant because three callers
#: have to agree that "we could not tell" is a real answer and not a falsy
#: stand-in for "no".
FOLLOW_UNKNOWN = "unknown"


def follow_state(label: Optional[str], *, count: int) -> dict[str, Any]:
    """Turn what the control said into a direction, or into an honest refusal.

    The gate this feeds may not proceed on ``unknown``. That is the whole
    reason the function returns a reason as well as a verdict: a caller that
    gets ``unknown`` has to be able to say WHY it stopped, and "the control had
    not rendered" and "there were three of them" want different answers from
    whoever reads it.
    """
    if count == 0:
        return {
            "state": FOLLOW_UNKNOWN,
            "why": (
                "no follow control rendered. On a job posting that means the "
                "page had not hydrated yet -- measured 2026-08-23, the same "
                "posting drew no control before it settled and Following "
                "after -- so this is NOT evidence that the company is "
                "unfollowed."
            ),
        }
    if count > 1:
        return {
            "state": FOLLOW_UNKNOWN,
            "why": (
                f"{count} follow controls rendered, so it is not possible to "
                "say which one belongs to this posting's employer. Choosing "
                "the first would be choosing by position."
            ),
        }
    known = FOLLOW_LABELS.get(str(label or "").strip())
    if known is None:
        return {
            "state": FOLLOW_UNKNOWN,
            "why": (
                f"the control is labelled {label!r}, which is neither of the "
                f"two measured states {sorted(FOLLOW_LABELS)}. LinkedIn has "
                "either relabelled it or drawn a control this reader has never "
                "seen, and guessing a direction from an unrecognised label is "
                "exactly the failure this returns instead of."
            ),
        }
    return {"state": known, "why": f"the control is labelled {label!r}"}


# ---------------------------------------------------------------------------
# Save state
# ---------------------------------------------------------------------------

#: The accessible name of the job-posting SAVE control in each state it has
#: been SEEN in, and what each one means. Deliberately shaped like
#: :data:`FOLLOW_LABELS` above, and deliberately HALF THE SIZE.
#:
#: ONE ENTRY, and the missing one is the honest centre of this whole feature.
#: Every capture this repo holds -- four postings, both hydration states, taken
#: on two different days -- renders ``aria-label="Save the job"``, the OFF
#: state. The ON state has never been observed and CANNOT be observed by
#: reading: he has nothing saved on the account, so there is no posting
#: anywhere that would draw it. The follow pair could be measured because a
#: company he already follows exists to load; the save pair has no equivalent.
#:
#: WHAT THAT COSTS, stated where the gap is rather than in a docstring
#: somewhere else: ``writes.perform`` anchors on the label for the state its
#: action is valid FROM, so ``save_job`` has an anchor and ``unsave_job`` does
#: not, and unsave refuses until this table gains its second row. THE FIRST
#: SUPERVISED SAVE IS THE MEASUREMENT -- ``perform`` re-reads the control after
#: it clicks and reports what it now says, precisely so that observation can be
#: written here. It is one line, and it is a line that must be MEASURED and not
#: guessed: ``"Saved"`` and ``"Unsave the job"`` are both plausible and this
#: server has seen neither.
SAVE_LABELS: dict[str, str] = {
    "Save the job": "not_saved",
}

#: Same contract as :data:`FOLLOW_UNKNOWN`: "could not tell" is an answer.
SAVE_UNKNOWN = "unknown"


def save_state(label: Optional[str], *, count: int) -> dict[str, Any]:
    """Turn what the SAVE control said into a state, or an honest refusal.

    Read this beside :func:`follow_state`, because the asymmetry between them
    is a measurement rather than an oversight. Follow knows both of its labels,
    so an unrecognised one means LinkedIn changed something. Save knows ONE, so
    an unrecognised label is ambiguous in a way follow's never is -- it could
    equally be the ON state finally being seen for the first time. This says
    so instead of collapsing the two into one word.
    """
    if count == 0:
        return {
            "state": SAVE_UNKNOWN,
            "why": (
                "no save control rendered in a state this reader recognises. "
                "That is NOT evidence the posting is unsaved, and it is not "
                "evidence it is saved either: with only the OFF label "
                "measured, 'the page has not hydrated' and 'the control is in "
                "the one state nobody has photographed' look identical from "
                "here."
            ),
        }
    if count > 1:
        return {
            "state": SAVE_UNKNOWN,
            "why": (
                f"{count} save controls rendered, so which one belongs to this "
                "posting cannot be settled. Choosing the first would be "
                "choosing by position."
            ),
        }
    known = SAVE_LABELS.get(str(label or "").strip())
    if known is None:
        return {
            "state": SAVE_UNKNOWN,
            "why": (
                f"the control is labelled {label!r}, which is not the one "
                f"measured state {sorted(SAVE_LABELS)}. This is the reading "
                "that most deserves a human: it is either LinkedIn relabelling "
                "the control, or it is the SAVED state being rendered for the "
                "first time on this account. Those want opposite responses, so "
                "this reader will not pick one."
            ),
        }
    return {"state": known, "why": f"the control is labelled {label!r}"}


# ---------------------------------------------------------------------------
# Apply route
# ---------------------------------------------------------------------------

#: The accessible name of the APPLY control in each route it has been SEEN in,
#: and which route each one means. Measured 2026-08-24 across thirteen job
#: captures; see ``dom.APPLY_LABELS_SEEN`` for the selector side.
#:
#: TWO ROUTES, AND THEY ARE DIFFERENT PROBLEMS. ``linkedin_apply`` keeps the
#: whole application inside LinkedIn; ``offsite`` hands the applicant to a
#: third-party ATS on somebody else's domain. Only the first could ever be
#: this server's to perform, and neither is performed today -- see
#: ``writes.SANCTIONED_WRITES['linkedin_apply_job']``.
#:
#: THE STRING "EASY APPLY" APPEARS IN ZERO ACCESSIBLE NAMES, and that is worth
#: stating because it is the name everybody knows the feature by. LinkedIn
#: renamed it: the control says "LinkedIn Apply to this job". A parser keyed on
#: "Easy Apply" matches nothing at all, which is the quiet kind of wrong.
APPLY_LABELS: dict[str, str] = {
    "LinkedIn Apply to this job": "linkedin_apply",
    "Apply on company website": "offsite",
}

#: The LinkedIn-hosted control's name is a PREFIX, not a fixed string, and this
#: was a live defect rather than a precaution.
#:
#: MEASURED 2026-08-24 on one posting, at two points in the SAME page load:
#:
#:     partially hydrated   "LinkedIn Apply to this job"
#:     fully settled        "LinkedIn Apply to <TITLE> at <COMPANY>"
#:
#: The dict above matches by exact equality, so once a posting finished
#: rendering, ``apply_route`` returned ``unknown`` for a perfectly ordinary
#: LinkedIn Apply posting. It failed SAFE -- refusing to classify rather than
#: misclassifying -- which is exactly why nobody noticed, and why the whole
#: test suite stayed green with the bug in it: every fixture carries the
#: partially-hydrated spelling, so no test ever showed the classifier the
#: string LinkedIn actually ends up serving.
#:
#: A prefix rather than a wider guess. It is the same shape as
#: ``writes.UNFOLLOW_ANCHOR_PREFIX``, and for the same reason: LinkedIn writes
#: variable content (there a Page's name, here the job title and employer) into
#: the tail of an otherwise fixed label. The tail is unpredictable; the head is
#: not. Everything that made this a CONJUNCTION still applies unchanged -- the
#: href must still be the posting's own apply url and the job id in it must
#: still match the posting's -- so widening the name test does not widen what
#: gets positively identified.
LINKEDIN_APPLY_PREFIX = "LinkedIn Apply to "

#: Same contract as :data:`FOLLOW_UNKNOWN` and :data:`SAVE_UNKNOWN`: "could not
#: tell" is an answer, and here it is the answer that matters most, because the
#: action gated on it cannot be taken back.
APPLY_UNKNOWN = "unknown"

#: The global-nav messaging badge, as LinkedIn spells it. Measured
#: 2026-08-24: ``aria-label="Messaging, 0 new notifications"``.
#:
#: It renders in the nav on ``/feed/``, an already-allowed read surface, so
#: reading it needs no boundary change and opens NOBODY'S conversation.
#:
#: **NEW IS NOT UNREAD, AND THIS FIELD SHIPPED CALLING IT UNREAD.** Measured
#: 2026-08-26 with a genuinely unread recruiter InMail on screen: the badge
#: read 0. The two quantities differ because the badge counts
#: NEW-SINCE-LAST-VISIT and RESETS WHEN THE MESSAGING TAB IS OPENED -- so
#: sitting in Messaging zeroes it while every conversation there stays
#: unread. It answers "has anything arrived since I last looked", which is a
#: real question and not the one the old name asked.
_MESSAGING_BADGE = re.compile(
    r'aria-label="Messaging,\s*([\d,]+)\s+new notification', re.I
)


def messaging_badge(html: str) -> dict[str, Any]:
    """How many messages arrived SINCE HE LAST OPENED MESSAGING. Not unread.

    THE DISTINCTION IS THE WHOLE POINT AND IT COST A WRONG ANSWER. This
    shipped returning ``unread``, and with an unread recruiter InMail visibly
    on screen it returned 0 -- because the badge had already reset when he
    opened the Messaging tab. A true statement ("the badge reads 0") wearing a
    false one ("you have no unread messages").

    THE DOCSTRING WAS ALREADY HONEST AND IT DID NOT HELP. It said "0 new" in
    the reason text, and the reviewer still read ``unread: 0`` as "nothing
    waiting" -- which is what any caller would do. **A field name is read far
    more often than the prose beside it**, so the fix had to be the name.

    ZERO IS A REAL ANSWER AND IS NOT THE SAME AS UNREADABLE, which is why this
    returns a dict rather than an int. A badge reading 0 and a badge that
    never rendered look identical to a caller that collapses them, and this
    package has already been bitten by exactly that: two attempts to measure
    whether reading a thread marks it read were INCONCLUSIVE because the badge
    sat at 0 with nowhere to fall -- a check that could not fail.
    """
    match = _MESSAGING_BADGE.search(html or "")
    if not match:
        return {
            "new_since_last_visit": None,
            "state": "unreadable",
            "why": (
                "no messaging badge rendered in the global nav. That is NOT "
                "the same as zero unread: the nav may not have hydrated, and "
                "this reader will not report a count it did not see."
            ),
        }
    raw = match.group(1).replace(",", "")
    try:
        count = int(raw)
    except ValueError:  # pragma: no cover - defensive
        return {
            "new_since_last_visit": None,
            "state": "unreadable",
            "why": f"the badge read {raw!r}, which is not a number.",
        }
    return {
        "new_since_last_visit": count,
        "state": "read",
        "why": (
            f"LinkedIn's own global-nav badge reads {count} new. Read off "
            "/feed/, which opens no conversation."
        ),
    }

#: LinkedIn's outbound interstitial. NOT an apply-specific url: the same
#: wrapper carries any external link on the page, so a capture holding two of
#: them has one that is an apply and one that is not. That is exactly why the
#: href alone may not classify -- it is corroboration for a label, never a
#: substitute for one.
_SAFETY_GO = re.compile(r"^https://www\.linkedin\.com/safety/go/\?", re.I)

#: The LinkedIn-hosted apply flow, addressed off the posting's own id.
_LINKEDIN_APPLY_HREF = re.compile(
    r"^https://www\.linkedin\.com/jobs/view/(\d{6,})/apply/(?:\?|$)", re.I
)

#: Hosts that are LinkedIn itself. An "off-site" destination that resolves back
#: here is not off-site, and calling it so would name the wrong owner for the
#: application.
_LINKEDIN_HOSTS = ("linkedin.com", "www.linkedin.com", "lnkd.in")


def decode_safety_go(href: Optional[str]) -> Optional[str]:
    """Recover the real destination from LinkedIn's outbound interstitial.

    Pure string work -- no network, no redirect followed. The wrapper carries
    the destination percent-encoded in its ``url`` parameter, including the
    dots of the hostname (``%2E``), so a naive split on ``.`` finds nothing and
    a naive read of the raw parameter yields a string that is not a url.

    Returns ``None`` rather than a guess when the parameter is missing or does
    not decode to an absolute http(s) url. A destination that cannot be named
    is one the operator cannot check, and an apply gate that cannot say WHOSE
    site it is sending him to has not identified the route.
    """
    raw = str(href or "")
    if not _SAFETY_GO.match(raw):
        return None
    query = urlsplit(raw).query
    values = parse_qs(query, keep_blank_values=True).get("url") or []
    for value in values:
        candidate = unquote(str(value or "")).strip()
        parts = urlsplit(candidate)
        if parts.scheme in {"http", "https"} and parts.netloc:
            return candidate
    return None


def _host_of(url: Optional[str]) -> Optional[str]:
    netloc = urlsplit(str(url or "")).netloc.strip().casefold()
    return netloc.split("@")[-1].split(":")[0] or None


def apply_route(
    label: Optional[str],
    href: Optional[str],
    *,
    count: int,
    job_id: Optional[str] = None,
    link_target: Optional[str] = None,
) -> dict[str, Any]:
    """Classify how one posting is applied to, or refuse to classify it.

    THREE ANSWERS, and the third is the one this function exists for.
    ``linkedin_apply`` and ``offsite`` are POSITIVE IDENTIFICATIONS, each
    requiring several independent fields to agree; anything else is
    :data:`APPLY_UNKNOWN`, with the reason. An apply is irreversible, so the
    standard here is higher than for a toggle: a route guessed wrong is an
    application sent to the wrong place, or an application sent at all when
    nobody could tell whether one would be.

    WHY A CONJUNCTION AND NOT THE OBVIOUS SINGLE FIELD. Each candidate
    discriminator was measured across thirteen captures and each fails alone:

    * ``data-view-name="job-apply-button"`` is present on ONE capture and
      absent from a fully hydrated off-site posting, so its absence carries no
      information whatever. It is not used here at all.
    * The ``/safety/go/`` href is a GENERIC outbound wrapper -- one capture
      holds two of them and only one is the apply control -- so href shape
      alone false-positives on an unrelated external link.
    * The accessible name is the strongest single field and is still not
      enough on its own: it is the one thing LinkedIn has already changed once
      on this surface (the feature is not called "Easy Apply" in the DOM).
    * The pre-hydration PAYLOAD is worse than useless: an off-site posting's
      own payload was measured carrying ``openSDUIApplyFlow=true`` on an
      ``OnsiteApplying`` state variant for the SAME job id. LinkedIn ships the
      whole apply state machine as a per-posting template, so a substring
      search over the payload classifies nothing. Only the RENDERED control
      answers, which is why this takes a label and an href rather than a page.

      WHERE THAT ONE WAS MEASURED, because a reader will look for it and not
      find it: in the RAW capture ``_audit/_probe-job-followed-company-pre.html``,
      which was gitignored and has since been DESTROYED -- it carried third
      parties' member urns and had no ongoing purpose once its counts were
      written down. So the claim is no longer re-verifiable from anything in
      this repo, by anyone, including its author. That was already half true:
      the file was never published, so no reader outside this machine could
      ever have checked it. The tracked fixtures cannot corroborate it either
      -- the sanitiser strips script payloads, so both following fixtures
      contain zero occurrences of either string and NO TEST IN THIS REPO
      GUARDS THIS PARAGRAPH. It is evidence for the design, not an asserted
      invariant, and it is labelled as such rather than left to look like the
      others. To re-establish it, re-capture: ``scripts/_probe_following.py``. What IS
      guarded, from the tracked fixtures: the hydrated off-site posting carries
      TWO ``/safety/go/`` urls of which only one is the apply control, which is
      the same argument made from a file anybody can open.
    """
    if count == 0:
        return {
            "route": APPLY_UNKNOWN,
            "why": (
                "no apply control rendered in a route this reader recognises. "
                "A posting that has not hydrated and a posting whose apply "
                "route is one nobody has seen look identical from here, so "
                "this is not evidence that the job cannot be applied to."
            ),
            "destination": None,
            "destination_host": None,
        }
    if count > 1:
        return {
            "route": APPLY_UNKNOWN,
            "why": (
                f"{count} apply controls rendered, so which one belongs to "
                "this posting cannot be settled. Choosing the first would be "
                "choosing by position, on the one action that cannot be undone."
            ),
            "destination": None,
            "destination_host": None,
        }

    name = str(label or "").strip()
    known = APPLY_LABELS.get(name)
    if known is None and name.startswith(LINKEDIN_APPLY_PREFIX):
        # The settled spelling, which carries the job title and employer in its
        # tail. See LINKEDIN_APPLY_PREFIX: the exact-match dict above misses
        # this, and missed it in production.
        known = "linkedin_apply"
    if known is None:
        return {
            "route": APPLY_UNKNOWN,
            "why": (
                f"the apply control is labelled {name!r}, which is neither of "
                f"the two measured routes {sorted(APPLY_LABELS)} nor a "
                f"{LINKEDIN_APPLY_PREFIX!r} name. LinkedIn has "
                "either relabelled it -- which it has done to this control "
                "before -- or drawn a third route this reader has never seen."
            ),
            "destination": None,
            "destination_host": None,
        }

    raw_href = str(href or "").strip()

    if known == "linkedin_apply":
        match = _LINKEDIN_APPLY_HREF.match(raw_href)
        if not match:
            return {
                "route": APPLY_UNKNOWN,
                "why": (
                    "the control claims the LinkedIn-hosted route but its href "
                    f"is {raw_href!r}, which is not this posting's own apply "
                    "url. The label and the destination must agree before a "
                    "route counts as identified."
                ),
                "destination": None,
                "destination_host": None,
            }
        found = match.group(1)
        if job_id is not None and str(job_id).strip() != found:
            return {
                "route": APPLY_UNKNOWN,
                "why": (
                    f"the apply control points at job {found}, and the posting "
                    f"being read is job {str(job_id).strip()}. A control that "
                    "belongs to a different posting is the clearest possible "
                    "reason to stop."
                ),
                "destination": None,
                "destination_host": None,
            }
        return {
            "route": "linkedin_apply",
            "why": (
                f"the control is labelled {name!r} and points at this "
                f"posting's own LinkedIn apply url ({raw_href!r}). The "
                "application would be filled in and submitted on LinkedIn."
            ),
            "destination": raw_href,
            "destination_host": _host_of(raw_href),
        }

    destination = decode_safety_go(raw_href)
    if destination is None:
        return {
            "route": APPLY_UNKNOWN,
            "why": (
                "the control claims the off-site route but its href "
                f"({raw_href!r}) is not LinkedIn's outbound wrapper carrying a "
                "decodable destination. A gate that cannot name whose site an "
                "application would be sent to has not identified the route."
            ),
            "destination": None,
            "destination_host": None,
        }
    host = _host_of(destination)
    if host is None or host in _LINKEDIN_HOSTS or host.endswith(".linkedin.com"):
        return {
            "route": APPLY_UNKNOWN,
            "why": (
                f"the off-site control decodes to {host!r}, which is LinkedIn "
                "itself. An off-site route that resolves back here is not "
                "off-site, and this reader will not name the wrong owner for "
                "an application."
            ),
            "destination": destination,
            "destination_host": host,
        }
    if str(link_target or "").strip() != "_blank":
        return {
            "route": APPLY_UNKNOWN,
            "why": (
                "the control claims the off-site route and decodes to "
                f"{host!r}, but it does not carry target=\"_blank\". Every "
                "off-site apply control measured does, and the outbound "
                "wrapper alone is not specific to applying -- the same wrapper "
                "carries unrelated external links on the same page."
            ),
            "destination": destination,
            "destination_host": host,
        }
    return {
        "route": "offsite",
        "why": (
            f"the control is labelled {name!r} and its outbound wrapper "
            f"decodes to {host!r}. The application would be made on that "
            "company's own applicant-tracking system, not on LinkedIn."
        ),
        "destination": destination,
        "destination_host": host,
    }


#: ``Click to stop following Ashgrove Systems`` -> ``Ashgrove Systems``. The
#: accessible name states the inverse action, which is where the reversibility
#: evidence for a follow comes from as well as the name.
_STOP_FOLLOWING = re.compile(r"^\s*Click to stop following\s+(.+?)\s*$", re.I)

#: ``58 Pages`` -- LinkedIn's own total, printed above a list it only partially
#: renders. Anchored to the END OF A LINE rather than floating anywhere in
#: ``main``, and read through ``_stated_total``, which insists it be the only
#: total the page states.
#:
#: WHAT WAS WRONG WITH IT. This was ``\b([\d,]+)\s+Pages?\b`` and its caller
#: took ``.search()`` -- the FIRST hit anywhere in ``main``, chosen by
#: position. ``Pages?`` matches the singular too, so an incidental ``1 Page``
#: above the heading became the total with a value of one, and one is a number
#: that twenty rendered rows clear. Downstream that is not a cosmetic misread:
#: it is a definite ``not_following`` about a Page he may well follow, printed
#: beside its own refutation -- "covers completely (20 of 1)".
#:
#: WHICH HALF OF THE FIX DOES THE WORK, measured rather than argued. The
#: UNIQUENESS RULE in ``_stated_total`` is what closes the hole. Every case in
#: the review's table carries a competing ``N Page(s)`` alongside the real
#: heading, so each comes back ambiguous and therefore unreadable EVEN UNDER
#: THE OLD PATTERN. The anchoring is a second bound, not the first one.
#:
#: WHY END-OF-LINE AND NOT WHOLE-LINE, which was written first and then
#: withdrawn. Whole-line is more PRECISE: it can dismiss ``You manage 2
#: Pages`` as not-a-heading and still recover the 58. End-of-line is more
#: CONSERVATIVE: it reads that same line as a competing claim and declines to
#: choose between them. This module is permitted to be wrong in exactly one
#: way -- by declining to answer -- so where the two disagree, the one that
#: declines is the one that belongs here. If LinkedIn grows a second phrase
#: stating a count, "I cannot tell which of these is this list's heading" is a
#: truer report than "I will take the one that owns its line".
#:
#: Verified against the surface rather than reasoned about: rendered and read,
#: all four Manage-Pages artefacts -- the two raw captures in ``_audit/`` and
#: the two sanitised fixtures -- put ``58 Pages`` alone on line 0 of ``main``'s
#: text and yield exactly one match under this pattern.
#:
#: The two RAW captures have since been destroyed (they carried third parties'
#: member urns). The two SANITISED fixtures are tracked and still carry the
#: shape, so unlike the payload claim above, this one remains guarded by tests
#: -- which is the difference between provenance and dependency, and the
#: reason destroying the raw half cost nothing here.
_PAGES_TOTAL = re.compile(r"([\d,]+)[ \t]+Pages?[ \t]*$", re.M)


def _stated_total(main_text: str) -> Optional[int]:
    """LinkedIn's own follow count, or nothing -- never a number off a phrase.

    Two lines stating DIFFERENT totals is not a tie to be broken by position.
    It means the reader cannot tell which heading it is looking at, and the
    honest total for a list whose own heading is ambiguous is no total at all.
    Taking the first, which is what ``.search()`` did, is choosing by position
    -- the same move ``follow_state`` already refuses when two follow controls
    render.

    Returning ``None`` costs an ``unknown`` downstream. That is the answer
    this module is built to be able to give.
    """
    seen: set[int] = set()
    for found in _PAGES_TOTAL.finditer(str(main_text or "")):
        try:
            seen.add(int(found.group(1).replace(",", "")))
        except ValueError:  # pragma: no cover - the regex already forbids this
            return None
    if len(seen) != 1:
        return None
    return seen.pop()


def _pages(count: int) -> str:
    """``58 Pages``, but ``1 Page``.

    LinkedIn's own heading agrees to the singular, and these strings quote that
    heading back at the operator as the evidence for a refusal. "says 1 Pages"
    reads as a string the server assembled rather than a number it read, which
    is the one impression a refusal cannot afford to give.
    """
    return f"{count} Page" if count == 1 else f"{count} Pages"


def _why_incomplete(rendered: int, total: Optional[int]) -> str:
    """Say WHICH way the reconciliation failed, because they are not one thing."""
    if total is None:
        return (
            "LinkedIn renders only the first rows of this list and loads the "
            "rest on scroll, which this server does not do -- one page load, "
            "whatever had drawn by then. Its own total could not be read at "
            "all. A name missing from `pages` is therefore NOT evidence that "
            "the Page is unfollowed."
        )
    if rendered > total:
        return (
            f"THE READ CONTRADICTS ITSELF: {rendered} rows were read while "
            f"LinkedIn's own heading says {_pages(total)}. More rows than the "
            "page claims means one of those two numbers is not what this "
            "reader took it for -- either something that is not a followed "
            "Page is being parsed as one, or the heading that was read is not "
            "this list's. A list that disagrees with itself settles a "
            "direction in NEITHER direction, so this read covers nothing and "
            "a name missing from `pages` is NOT evidence that the Page is "
            "unfollowed."
        )
    return (
        "LinkedIn renders only the first rows of this list and loads the rest "
        "on scroll, which this server does not do -- one page load, whatever "
        f"had drawn by then. It says {_pages(total)} and rendered {rendered}. A "
        "name missing from `pages` is therefore NOT evidence that the Page is "
        "unfollowed."
    )


def parse_followed_pages(
    rows: Iterable[dict[str, Any]], main_text: str
) -> dict[str, Any]:
    """Shape the Manage-Pages read, and refuse to overstate what it covers.

    THE HAZARD THIS EXISTS FOR, measured 2026-08-23: LinkedIn renders TWENTY
    rows under a heading that says ``58 Pages``, and only TEN before the page
    settles. So "not in the list" means "not followed" only when the list is
    complete, and on this surface it never is. A reader that skipped the
    reconciliation would answer "you do not follow them" about thirty-eight
    companies it had simply not been shown -- and would answer it to a confirm
    gate, which would then offer to follow a company he already follows.
    """
    pages: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        match = _STOP_FOLLOWING.match(str(row.get("label") or ""))
        if not match:
            continue
        name = match.group(1).strip()
        if not name or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        page_id = None
        found = re.search(r"/company/([A-Za-z0-9\-_%]+)", str(row.get("href") or ""))
        if found:
            page_id = found.group(1)
        pages.append({"name": name, "id": page_id})

    total = _stated_total(main_text)
    rendered = len(pages)

    # EQUALITY, NOT `>=`, AND THAT IS THE WHOLE OF THE SECOND HAZARD. `>=`
    # cannot tell "we were shown everything" from "the number we read is not
    # this list's", and it resolves the second into the FIRST -- the reading
    # that licenses a definite `not_following`. Twenty rows against a total of
    # one used to come back complete, printing its own refutation as the
    # reason: "covers completely (20 of 1)". A human might notice that; the
    # confirm gate downstream reads `state` and never sees it. So more rows
    # than the stated total is a CONTRADICTION and covers nothing, which is
    # the same reconciliation `writes._read_saved_state` already applies to
    # the tracker in both directions.
    complete = total is not None and rendered == total
    return {
        "pages": pages,
        "rendered": rendered,
        "total_followed": total,
        "complete": complete,
        "why_incomplete": None if complete else _why_incomplete(rendered, total),
    }


def followed_page_state(query: str, parsed: dict[str, Any]) -> dict[str, Any]:
    """Answer "do I follow this Page?" in three values, never in two."""
    wanted = str(query or "").strip().casefold()
    for page in parsed.get("pages", []):
        if str(page.get("name", "")).casefold() == wanted or (
            page.get("id") and str(page["id"]).casefold() == wanted
        ):
            return {
                "state": "following",
                "why": f"{page['name']!r} is in the rendered list",
                "matched": page,
            }
    if parsed.get("complete"):
        return {
            "state": "not_following",
            "why": (
                f"{query!r} is absent from a list this read covers completely "
                f"({parsed.get('rendered')} of {parsed.get('total_followed')})"
            ),
            "matched": None,
        }
    return {
        "state": FOLLOW_UNKNOWN,
        "why": (
            f"{query!r} is absent from the rows that rendered, but the read "
            "does not cover the whole list. " + str(parsed.get("why_incomplete"))
        ),
        "matched": None,
    }


# ---------------------------------------------------------------------------
# Open To Work
# ---------------------------------------------------------------------------

#: ``Open to work `` + MIDDLE_DOT + `` Recruiters only``. The audience is the
#: half that matters and LinkedIn prints it verbatim, which is the only reason
#: a confirm gate can name it rather than describe it.
_OPEN_TO_WORK = re.compile(
    r"^\s*Open to work\s*" + re.escape(MIDDLE_DOT) + r"\s*(.+?)\s*$", re.I
)

#: What each audience string MEANS when a profile change would be visible to
#: a current employer. The
#: point of the mapping is that a gate has to state WHO CAN SEE IT rather than
#: repeat LinkedIn's four words back at him.
OPEN_TO_WORK_AUDIENCES: dict[str, str] = {
    "recruiters only": (
        "visible only to recruiters using LinkedIn Recruiter. No badge is drawn "
        "on the photo, so an employer browsing the profile does not see it -- "
        "though "
        "LinkedIn itself states it cannot guarantee that recruiters at your own "
        "company are excluded."
    ),
    "all linkedin members": (
        "PUBLIC. A green #OpenToWork frame is drawn on your profile photo and "
        "everyone who can see your profile can see it, INCLUDING YOUR CURRENT "
        "EMPLOYER AND COLLEAGUES."
    ),
}


def parse_open_to_work(lines: Iterable[str]) -> dict[str, Any]:
    """Read the Open To Work state and its AUDIENCE off the profile topcard.

    Returns ``on=None`` when nothing could be read, which is not the same as
    ``on=False``: the second is a claim that he is not sharing, and this reader
    is not entitled to make it from a page that may simply not have drawn the
    card.
    """
    for line in lines:
        match = _OPEN_TO_WORK.match(str(line or ""))
        if not match:
            continue
        audience = match.group(1).strip()
        return {
            "on": True,
            "audience": audience,
            "who_can_see_it": OPEN_TO_WORK_AUDIENCES.get(
                audience.casefold(),
                "UNRECOGNISED audience string -- this reader has only ever seen "
                f"{sorted(OPEN_TO_WORK_AUDIENCES)}, so it will not say who can "
                "see it.",
            ),
        }
    return {
        "on": None,
        "audience": None,
        "who_can_see_it": (
            "not readable: no 'Open to work' line rendered. That is not the "
            "same as it being off -- the card may not have drawn."
        ),
    }


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


# ---------------------------------------------------------------------------
# The messaging surface
# ---------------------------------------------------------------------------

#: How LinkedIn labels each row of the conversation list. Measured on the live
#: surface: ``aria-label="Select conversation with <NAME>"``.
_CONVERSATION_ROW = re.compile(r'aria-label="Select conversation with ([^"]+)"')

#: Words LinkedIn uses to mark a row unread. Measured: ``UNREAD``, ``Unread``,
#: ``unread`` and the class token ``messaging-remove-unread-blue-background``.
_UNREAD_MARKER = re.compile(r"\bunread\b", re.I)

#: Anything that would let a caller send. Counted so the answer to "did
#: reading put a compose box on the page" is a NUMBER rather than a promise.
_SEND_SURFACES = (
    ("contenteditable", re.compile(r'contenteditable="true"')),
    ("send_controls", re.compile(r'(?i)aria-label="[^"]*\bsend\b[^"]*"')),
    ("forms", re.compile(r"<form\b")),
)

#: Names are replaced with this unless the caller opts in. His own inbox, his
#: own correspondents -- but the output lands in a model's context and in
#: transcripts, and a name there outlives the question that fetched it.
NAME_PLACEHOLDER = "<NAME>"


def _conversation_rows(html: str) -> list[dict[str, Any]]:
    """One record per conversation, with its unread state ATTACHED.

    WHY THIS IS SEGMENTED RATHER THAN COUNTED. The first version counted names
    and unread markers separately and returned "10 conversations, 4 unread
    markers" -- true, and useless: it told him four people were waiting
    without telling him WHICH four, so he still had to open LinkedIn to find
    out, which is most of what this tool exists to spare him.

    The marker and the name sit on the same row, so they are read together.
    The row boundary is taken as the span between one conversation label and
    the next -- LinkedIn nests these deeply and by hashed class names, so
    slicing on the labels themselves is stabler than guessing a container
    selector that changes with every redeploy.

    ORDER IS PRESERVED, and that is load-bearing even when names are redacted:
    "rows 1 and 4 of 10 are unread" is actionable in a way that "4 unread" is
    not.
    """
    text = html or ""
    marks = list(_CONVERSATION_ROW.finditer(text))
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, match in enumerate(marks):
        name = match.group(1).strip()
        if name in seen:
            continue
        seen.add(name)
        # The row runs from this label to the next one. The tail row runs to
        # a bounded distance rather than to the end of the document, so the
        # page footer cannot mark the last conversation unread.
        start = match.start()
        end = marks[i + 1].start() if i + 1 < len(marks) else min(len(text), match.end() + 4000)
        segment = text[start:end]
        rows.append(
            {
                "position": len(rows) + 1,
                "name": name,
                "unread": bool(_UNREAD_MARKER.search(segment)),
            }
        )
    return rows


def messaging_overview(
    html: str, landed_url: str, *, include_names: bool = False
) -> dict[str, Any]:
    """What the messaging surface holds, and what opening it cost.

    THE COST IS A FIELD, NOT A FOOTNOTE. Asking LinkedIn for ``/messaging/``
    does not stay on a list: it redirects into ONE SPECIFIC CONVERSATION that
    LinkedIn, not the caller, chooses. So every call opens somebody's thread,
    and ``thread_opened`` says so with the evidence -- the landed url -- rather
    than leaving a caller to discover it.

    WHETHER THAT MARKS THE MESSAGE READ IS UNMEASURED, and after three
    attempts it is believed to be unmeasurable from outside. The nav badge
    counts NEW-SINCE-LAST-VISIT and resets when the tab is opened, so it
    cannot witness a read; the per-row unread markers live on this very page,
    which cannot be reached without the redirect. **The only signal that would
    settle it requires performing the act being measured.**

    UNREAD IS PAIRED TO THE ROW, not counted beside it. An earlier version
    returned a conversation count and a separate marker count, which told him
    four people were waiting without telling him which four -- so he still had
    to open LinkedIn, which is most of what this exists to spare him.

    NAMES ARE OFF BY DEFAULT and the pairing survives the redaction: position
    plus unread state is actionable even without identities.
    """
    text = html or ""
    rows = _conversation_rows(text)
    sends = {label: len(pattern.findall(text)) for label, pattern in _SEND_SURFACES}
    in_document = len(_UNREAD_MARKER.findall(text))
    in_rows = sum(1 for r in rows if r["unread"])
    on_a_thread = "/messaging/thread/" in (landed_url or "")

    conversations = [
        {
            "position": row["position"],
            "name": row["name"] if include_names else NAME_PLACEHOLDER,
            "unread": row["unread"],
        }
        for row in rows
    ]

    return {
        "conversations": len(rows),
        "unread": in_rows,
        "rows": conversations,
        # BOTH COUNTS, AND THE DISAGREEMENT NAMED. An earlier version counted
        # the word "unread" across the WHOLE document and reported 4; scoping
        # it to conversation rows reports 0 on the same account. Rather than
        # pick which is right, both are shown -- because the honest answer is
        # that they measure different things and only one of them answers
        # "who is waiting".
        #
        # The document count is knowingly LOOSE: the filter pill above the
        # list is itself labelled "Unread", class names contain the word, and
        # so does the payload. So a document count above the row count is
        # expected and is NOT evidence of missed conversations. It is evidence
        # the word appears in furniture.
        "unread_markers_in_document": in_document,
        "marker_reconciliation": (
            "row-scoped and document-wide counts agree"
            if in_document == in_rows
            else (
                f"{in_document} occurrences of 'unread' in the page, "
                f"{in_rows} on conversation ROWS. The gap is expected: the "
                "filter pill is labelled Unread, and the word appears in "
                "class names and payload. The ROW count is the one that "
                "answers who is waiting. If a conversation you can SEE marked "
                "unread in the product reads false here, that is a real "
                "under-count and the row scoping is wrong -- report it."
            )
        ),
        "send_surfaces": sends,
        "thread_opened": {
            "opened": on_a_thread,
            "landed_url": redact_thread_id(landed_url),
            "why": (
                "LinkedIn redirected the request into one specific conversation. "
                "The caller did not choose which -- LinkedIn did."
                if on_a_thread
                else "the surface stayed on the list this time, which is not "
                "the measured behaviour and is worth noticing."
            ),
            "marks_it_read": (
                "UNMEASURED, and believed unmeasurable from outside. The nav "
                "badge counts new-since-last-visit and resets on tab open, so "
                "it cannot witness a read; the per-row unread markers are on "
                "this page, which cannot be reached without this redirect. "
                "Settling it requires performing the act being measured."
            ),
        },
        "names_included": bool(include_names),
        "completeness": (
            "This is ONE PAGE of the conversation list, and whether LinkedIn "
            "lists InMails here or on a separate surface is UNMEASURED -- a "
            "recruiter InMail was seen in the product that did not appear in "
            "these rows. So this count is a floor, not a total. Pass a filter "
            "to narrow it; do not read it as everything waiting."
        ),
    }


def redact_thread_id(url: Optional[str]) -> Optional[str]:
    """A messaging url with the conversation identifier removed.

    The thread id names one private conversation. It is of no use to a caller
    -- nothing here accepts it -- and it is exactly the kind of value that
    should not sit in a transcript.
    """
    if not url:
        return url
    return re.sub(r"(/messaging/thread/)[^/?#]+", r"\1<THREAD-ID>", url)


#: The filter pills LinkedIn draws above the conversation list. Their names
#: are taken from the product UI; what each one DOES is read off the page
#: rather than assumed, exactly as apply_route reads the apply anchor instead
#: of guessing the apply url.
_FILTER_NAMES = ("focused", "other", "unread", "jobs", "connections", "inmail", "starred")

#: Any element carrying one of those names, with whatever destination it has.
#: Deliberately broad: a control that turns out to be a <button> with no href
#: is a FINDING (the filter is client-side state, so InMails are unreachable
#: without interacting), not a parse failure to be hidden.
_LABELLED_CONTROL = re.compile(r"<(a|button)([^>]*)>([^<]{0,60})", re.I)
_ARIA = re.compile(r'aria-label="([^"]*)"')
_HREF = re.compile(r'href="([^"]*)"')


def messaging_filters(html: str) -> dict[str, Any]:
    """What the filter pills are, and where each one actually goes.

    THE INMAIL QUESTION THIS EXISTS TO SETTLE. A recruiter InMail was visible
    in the product under its Unread filter and did not appear in the rows this
    server reads. Either it sits below the page, or InMails are filed on a
    surface of their own. Those are different findings and guessing between
    them would make every count this tool prints untrustworthy.

    So the controls are READ. If a pill is an anchor, its href names the
    surface and the filter parameter is measured rather than invented. If it
    is a button with no href, the filtering is client-side state and InMails
    are NOT reachable by navigation at all -- which is equally a finding, and
    the honest answer is then that this server cannot see them without
    interacting with the page.
    """
    text = html or ""
    found: dict[str, dict[str, Any]] = {}
    for match in _LABELLED_CONTROL.finditer(text):
        tag, attrs, inner = match.groups()
        aria = _ARIA.search(attrs or "")
        # The accessible name if there is one, else the visible text. Real
        # LinkedIn pills nest spans, so inner text is often empty and the
        # aria-label is the only thing carrying the word.
        label = ((aria.group(1) if aria else "") + " " + (inner or "")).strip().lower()
        for name in _FILTER_NAMES:
            if name and name in label and name not in found:
                href = _HREF.search(attrs or "")
                found[name] = {
                    "tag": tag.lower(),
                    "href": href.group(1) if href else None,
                    "navigable": bool(href),
                }
    navigable = [n for n, v in found.items() if v["navigable"]]
    return {
        "filters_seen": sorted(found),
        "detail": found,
        "navigable_filters": sorted(navigable),
        "verdict": (
            "filter pills carry hrefs, so the filter surface is reachable by "
            "navigation and the parameter is now MEASURED rather than guessed"
            if navigable
            else "no filter pill carries an href on this page. Either they did "
            "not render, or filtering is client-side state -- in which case "
            "InMails are not reachable from this server without interacting "
            "with the page, which it does not do."
        ),
    }
