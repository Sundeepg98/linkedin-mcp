"""WHAT "SHOW MORE ANALYTICS" REVEALS on his profile-views page, read.

The decided reveal (:mod:`linkedin_server.reveal`) presses the button; this
module reads what it drew. Measured 2026-09-23 from a live capture taken
straight after the press (``_audit/2026-09-23-live-lane-session-1.md`` Entry
7), by headings and line shapes only:

    Highlights   7 lines: the heading, then three value/label pairs --
                 <value> / "Top location", <value> / "Top industry",
                 <value> / "Top company"; no numbers
    Details      7 lines: the heading, the sub-heading "Companies", then five
                 "<company> (<n>%)" entries

## WHAT IS PUBLISHED, AND WHY NO NAME IS REDACTED HERE

The values are facts about his viewers IN AGGREGATE: the most common
location, industry and company, and each company's share. The tool this is
wired into, ``linkedin_who_viewed_me``, already returns every viewer by NAME
and HEADLINE -- which carries their employer and title -- by default. An
aggregate over those same people discloses nothing about any one of them that
the tool does not already return, so the census convention for OTHER people's
demographics (shape plus ``census_redact_rare``) is not applied, and the
reason is stated here so it can be refuted: **if this reader is ever wired to
a surface whose rows are NOT otherwise returned, this paragraph no longer
holds and the redaction is owed.**

## WHAT IS NOT CLAIMED

The share of a company is a percentage of a base the section does not print.
No count is derived from it. A line this reader cannot place is COUNTED in
``unparsed_lines`` and never guessed at; a section it cannot find is absent
from ``sections_found`` rather than reported empty.

This module reads and presses nothing: locators and ``inner_text`` only, no
injected script.
"""
from __future__ import annotations

import re
from typing import Any, Optional

#: The two section headings, normalised.
SECTIONS: tuple[str, ...] = ("highlights", "details")

#: The Highlights labels, normalised, and the key each value is published under.
HIGHLIGHT_LABELS: dict[str, str] = {
    "top location": "top_location",
    "top industry": "top_industry",
    "top company": "top_company",
}

#: A Details entry: a name, then a percentage in parentheses.
DETAILS_ENTRY = re.compile(r"^(?P<name>.+?)\s*\(\s*(?P<pct>\d{1,3}(?:\.\d+)?)\s*%\s*\)$")

#: How far up from a heading to look for its section: the first ancestor whose
#: text is longer than the heading by this margin. Measured: within 4 levels.
CLIMB_LEVELS = 4
CLIMB_MARGIN = 40

_NOT_ALNUM = re.compile(r"[^a-z0-9]+")


def normalised(text: Any) -> str:
    """Lower-case; every run outside ``[a-z0-9]`` becomes one space. PURE."""
    return _NOT_ALNUM.sub(" ", str(text or "").lower()).strip()


def parse_highlights(lines: list[str]) -> tuple[dict[str, Optional[str]], int]:
    """Value/label pairs after the heading. PURE. Returns (values, unparsed)."""
    values: dict[str, Optional[str]] = {key: None for key in HIGHLIGHT_LABELS.values()}
    used: set[int] = {0}
    for index, line in enumerate(lines):
        key = HIGHLIGHT_LABELS.get(normalised(line))
        if key is None or index == 0:
            continue
        values[key] = lines[index - 1].strip()
        used.update({index, index - 1})
    return values, len(lines) - len(used)


def parse_details(lines: list[str]) -> tuple[dict[str, Any], int]:
    """The sub-heading and its "<name> (<n>%)" entries. PURE."""
    entries: list[dict[str, Any]] = []
    unparsed = 0
    heading: Optional[str] = None
    for index, line in enumerate(lines):
        if index == 0:
            continue
        found = DETAILS_ENTRY.match(line.strip())
        if found:
            entries.append({"name": found.group("name").strip(), "percent": float(found.group("pct"))})
        elif heading is None and not entries:
            heading = normalised(line)
        else:
            unparsed += 1
    return {"heading": heading, "entries": entries}, unparsed


async def _section_lines(heading: Any) -> list[str]:
    """The text lines of the section a heading opens. READS ONLY."""
    name_length = len((await heading.inner_text()).strip())
    node = heading
    for _level in range(CLIMB_LEVELS):
        node = node.locator("xpath=..")
        text = await node.inner_text()
        if len(text.strip()) >= name_length + CLIMB_MARGIN:
            break
    return [line.strip() for line in (await node.inner_text()).split("\n") if line.strip()]


async def read_profile_views_more_insights(page: Any) -> dict[str, Any]:
    """Read the Highlights and Details sections, if drawn. READS ONLY."""
    out: dict[str, Any] = {
        "sections_found": [],
        "highlights": None,
        "details": None,
        "unparsed_lines": 0,
    }
    headings = page.locator("main").locator("h1, h2, h3, h4, h5, h6, [role=heading]")
    for position in range(int(await headings.count())):
        heading = headings.nth(position)
        name = normalised(await heading.inner_text())
        if name not in SECTIONS or name in out["sections_found"]:
            continue
        lines = await _section_lines(heading)
        out["sections_found"].append(name)
        if name == "highlights":
            values, unparsed = parse_highlights(lines)
            out["highlights"] = values
        else:
            values_details, unparsed = parse_details(lines)
            out["details"] = values_details
        out["unparsed_lines"] += unparsed
    return out
