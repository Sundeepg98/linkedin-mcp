"""The tool surface: nine tools, every one of them a read.

There is no write path in this package. Not a disabled one, not a stubbed one,
not one behind a flag. Nothing here applies to a job, saves a job, sends a
message, edits the profile, toggles Open To Work, or marks anything read on
purpose. ``readonly.py`` holds the machinery that keeps that true, and
``tests/test_readonly.py`` runs it against this file.

One documented exception, and it is a side effect rather than an action:
opening the notifications page clears LinkedIn's unread badge, exactly as it
would if the operator opened the page himself. It is called out in that
tool's docstring because a read that changes something has to say so.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from urllib.parse import urlencode

from fastmcp import FastMCP

from linkedin_own_server import dom, shape
from linkedin_own_server.auth import (
    assert_not_authwall,
    check_auth,
    login_via_browser,
)
from linkedin_own_server.browser import BROWSER
from linkedin_own_server.config import (
    BASE_URL,
    DEFAULT_LIMIT,
    IDLE_CLOSE_S,
    LOGIN_WAIT_S,
    MAX_LIMIT,
    MAX_NAVIGATIONS_PER_CALL,
    MIN_NAVIGATION_INTERVAL_S,
    NOTIFICATIONS_DEFAULT_LIMIT,
    NOTIFICATIONS_MAX_LIMIT,
    SEARCH_DEFAULT_LIMIT,
    SEARCH_MAX_LIMIT,
    SERVER_NAME,
    SERVER_VERSION,
    CHROME_PROFILE,
)
from linkedin_own_server.errors import ExtractionFailedError, LinkedInReaderError
from linkedin_own_server.profile_lock import held_by

mcp = FastMCP(
    name=SERVER_NAME,
    instructions=(
        "Read-only window onto the operator's OWN LinkedIn account, driven by "
        "his own signed-in browser on his own machine. Every tool reads; none "
        "of them changes anything on LinkedIn. There is no apply, no save, no "
        "message, no connection request, no profile edit -- those are out of "
        "scope by design, so do not look for them or suggest they exist. "
        "Start with linkedin_auth_status; if it says false, the operator must "
        "call linkedin_login_browser and sign in himself. The highest-signal "
        "tool is linkedin_who_viewed_me: where the account has Premium Career, so it "
        "reaches back 365 days. Each call loads exactly one page, so ask for "
        "one thing at a time rather than sweeping."
    ),
)


# ---------------------------------------------------------------------------
# Shared plumbing
# ---------------------------------------------------------------------------


def _error(exc: Exception) -> dict[str, Any]:
    """Report a failure as a failure, with everything needed to act on it."""
    if isinstance(exc, LinkedInReaderError):
        out: dict[str, Any] = {"error": exc.kind, "message": str(exc)}
        url = getattr(exc, "url", "")
        if url:
            out["url"] = url
        hint = getattr(exc, "hint", "")
        if hint:
            out["hint"] = hint
        return out
    return {"error": "unexpected", "message": f"{type(exc).__name__}: {exc}"}


def _clamp(value: Optional[int], default: int, maximum: int) -> int:
    if value is None:
        return default
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(value, maximum))


async def _read_cards(
    url: str,
    *,
    href_pattern: str,
    parser,
    limit: int,
    surface: str,
    allow_empty: bool = False,
) -> dict[str, Any]:
    """One page load, one harvest, one shaping pass. The shape of every list tool."""
    async with BROWSER.session() as page:
        final_url = await BROWSER.goto(page, url)
        assert_not_authwall(final_url, surface=surface)
        records = await dom.harvest_linked_cards(
            page, href_pattern=href_pattern, max_items=limit * 3
        )
        if not allow_empty:
            dom.require_rows(records, url=final_url, surface=surface)
        rows, dropped = dom.parse_all(records, parser)
        return shape.envelope(
            rows, limit=limit, source_url=final_url, dropped=dropped
        )


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


@mcp.tool()
async def linkedin_auth_status() -> dict[str, Any]:
    """Report whether there is a live LinkedIn session, measured not guessed.

    The verdict comes from an authenticated request: GET /voyager/api/me, the
    same identity call LinkedIn's own web app makes on page load. A session
    cookie sitting in the profile proves nothing and is never treated as an
    answer -- LinkedIn hands cookies to signed-out visitors too.

    Three outcomes, deliberately:
      * authenticated true  -- the endpoint returned an identity.
      * authenticated false -- the endpoint refused, or the feed redirected
        to LinkedIn's signed-out wall.
      * authenticated null  -- neither could be established. Unknown is
        reported as unknown rather than collapsed into "signed out".

    Costs up to two requests: the identity call, plus one feed load used only
    to turn an inconclusive answer into a definite "false".
    """
    try:
        async with BROWSER.session() as page:
            return await check_auth(page, corroborate=True)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_login_browser(wait_seconds: int = LOGIN_WAIT_S) -> dict[str, Any]:
    """Open LinkedIn's sign-in page and wait for you to sign in yourself.

    This server never sees, types, stores or transmits a password. It opens a
    browser window at linkedin.com/login; you type into that window; the
    persistent Chrome profile keeps the session afterwards, so this is a
    one-time step until LinkedIn expires it.

    The window stays open until the identity endpoint confirms a real session,
    the window is closed, or wait_seconds runs out. A cookie appearing does
    not end the wait -- it only causes the endpoint to be asked again. On
    timeout the result is authenticated false with a reason, never an
    optimistic success.

    Args:
        wait_seconds: how long to leave the window open for you. Default 300.
    """
    try:
        async with BROWSER.session() as page:
            return await login_via_browser(page, wait_seconds=int(wait_seconds))
    except Exception as exc:
        return _error(exc)


# ---------------------------------------------------------------------------
# The reads
# ---------------------------------------------------------------------------


@mcp.tool()
async def linkedin_who_viewed_me(limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """List the people who viewed your profile, most recent first.

    The highest-intent signal in a job search: someone who opened your profile
    has already spent attention on you. Where the account has Premium Career, this list reaches
    back 365 days rather than the free tier's five viewers.

    Rows carry name, headline, when the view happened, and a profile link.
    Viewers browsing in private mode appear as LinkedIn shows them -- as
    anonymous rows, flagged with "anonymous": true and no link. This server
    does not try to work out who they are.

    Reads the Premium analytics page; if that renders nothing it falls back
    once to the classic profile-views page, and reports pages_loaded: 2.
    Nothing is fetched about these people beyond the row LinkedIn already
    displays to you.

    Args:
        limit: maximum rows to return (default 25, max 100).
    """
    limit = _clamp(limit, DEFAULT_LIMIT, MAX_LIMIT)
    urls = [
        f"{BASE_URL}/analytics/profile-views/",
        f"{BASE_URL}/me/profile-views/",
    ]
    try:
        async with BROWSER.session() as page:
            last_url = ""
            for attempt, url in enumerate(urls[:MAX_NAVIGATIONS_PER_CALL], start=1):
                last_url = await BROWSER.goto(page, url)
                assert_not_authwall(last_url, surface="profile views")
                records = await dom.harvest_linked_cards(
                    page, href_pattern=dom.PERSON_HREF, max_items=limit * 3
                )
                rows, dropped = dom.parse_all(records, shape.parse_person_card)
                if rows:
                    return shape.envelope(
                        rows,
                        limit=limit,
                        source_url=last_url,
                        pages_loaded=attempt,
                        dropped=dropped,
                    )
            raise ExtractionFailedError(
                "no profile viewers could be read from either the analytics or "
                "the classic profile-views page. If you genuinely have no "
                "viewers this is what an empty list looks like; if you know "
                "there are some, LinkedIn has changed this surface.",
                url=last_url,
                hint="open the url yourself and compare with what this reports",
            )
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_my_applications(limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """List the jobs you have applied to on LinkedIn, with their status.

    Reads your own My Items > Applied list. Each row carries title, company,
    location, the status LinkedIn shows (applied, application viewed, resume
    downloaded, no longer accepting applications) and how long ago, plus the
    job id and link.

    Status is whatever LinkedIn displays; this server does not infer, score or
    chase anything, and it cannot see applications you made anywhere else.

    Args:
        limit: maximum rows to return (default 25, max 100).
    """
    limit = _clamp(limit, DEFAULT_LIMIT, MAX_LIMIT)
    try:
        return await _read_cards(
            f"{BASE_URL}/my-items/saved-jobs/?cardType=APPLIED",
            href_pattern=dom.JOB_HREF,
            parser=shape.parse_job_card,
            limit=limit,
            surface="applied jobs",
        )
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_saved_jobs(limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """List the jobs you have bookmarked on LinkedIn.

    Reads your own My Items > Saved list: title, company, location, when it
    was posted where LinkedIn shows it, and the job link.

    Read-only in both directions -- this lists what you saved and has no way
    to add to or remove from the list.

    Args:
        limit: maximum rows to return (default 25, max 100).
    """
    limit = _clamp(limit, DEFAULT_LIMIT, MAX_LIMIT)
    try:
        return await _read_cards(
            f"{BASE_URL}/my-items/saved-jobs/?cardType=SAVED",
            href_pattern=dom.JOB_HREF,
            parser=shape.parse_job_card,
            limit=limit,
            surface="saved jobs",
        )
    except Exception as exc:
        return _error(exc)


_DATE_POSTED = {
    "any": None,
    "past_24h": "r86400",
    "past_week": "r604800",
    "past_month": "r2592000",
}
_WORKPLACE = {"any": None, "on_site": "1", "remote": "2", "hybrid": "3"}
_EXPERIENCE = {
    "internship": "1",
    "entry": "2",
    "associate": "3",
    "mid_senior": "4",
    "director": "5",
    "executive": "6",
}


@mcp.tool()
async def linkedin_search_jobs(
    keywords: str,
    location: str = "",
    remote: str = "any",
    date_posted: str = "any",
    experience_level: str = "",
    sort_by: str = "relevance",
    start: int = 0,
    limit: int = SEARCH_DEFAULT_LIMIT,
) -> dict[str, Any]:
    """Search LinkedIn jobs with filters, returning one page of results.

    Runs the search LinkedIn's own jobs page runs and reads the rendered
    results: title, company, location, job id and link.

    One page load per call, no scrolling and no auto-paging -- LinkedIn puts
    roughly 25 results on a page, so ask for the next page deliberately with
    start=25, start=50 and so on. capped in the result tells you the limit
    trimmed the rows, and page_had tells you how many the page actually held.

    Note that LinkedIn records searches in your own recent-search history,
    exactly as it would if you typed the query on the site. That is the only
    trace a search leaves, and it is on your account, not anyone else's.

    Args:
        keywords: what to search for, e.g. "senior node.js engineer".
        location: city, region or country. Empty means LinkedIn's default.
        remote: any | on_site | remote | hybrid.
        date_posted: any | past_24h | past_week | past_month.
        experience_level: comma-separated from internship, entry, associate,
            mid_senior, director, executive. Empty means no filter.
        sort_by: relevance | date.
        start: result offset for manual paging (0, 25, 50 ...).
        limit: maximum rows to return (default 25, max 50).
    """
    limit = _clamp(limit, SEARCH_DEFAULT_LIMIT, SEARCH_MAX_LIMIT)
    try:
        if not (keywords or "").strip():
            return {
                "error": "bad_argument",
                "message": "keywords is required -- an empty search is a page of noise.",
            }

        params: list[tuple[str, str]] = [("keywords", keywords.strip())]
        if location.strip():
            params.append(("location", location.strip()))

        workplace = _WORKPLACE.get(remote.strip().lower(), "sentinel")
        if workplace == "sentinel":
            return {
                "error": "bad_argument",
                "message": f"remote must be one of {sorted(_WORKPLACE)}, got {remote!r}",
            }
        if workplace:
            params.append(("f_WT", workplace))

        tpr = _DATE_POSTED.get(date_posted.strip().lower(), "sentinel")
        if tpr == "sentinel":
            return {
                "error": "bad_argument",
                "message": (
                    f"date_posted must be one of {sorted(_DATE_POSTED)}, "
                    f"got {date_posted!r}"
                ),
            }
        if tpr:
            params.append(("f_TPR", tpr))

        levels = [p.strip().lower() for p in experience_level.split(",") if p.strip()]
        unknown = [p for p in levels if p not in _EXPERIENCE]
        if unknown:
            return {
                "error": "bad_argument",
                "message": (
                    f"unknown experience_level {unknown}; choose from "
                    f"{sorted(_EXPERIENCE)}"
                ),
            }
        if levels:
            params.append(("f_E", ",".join(_EXPERIENCE[p] for p in levels)))

        if sort_by.strip().lower() == "date":
            params.append(("sortBy", "DD"))
        elif sort_by.strip().lower() not in ("", "relevance"):
            return {
                "error": "bad_argument",
                "message": f"sort_by must be relevance or date, got {sort_by!r}",
            }

        start = max(0, int(start))
        if start:
            params.append(("start", str(start)))

        url = f"{BASE_URL}/jobs/search/?{urlencode(params)}"
        result = await _read_cards(
            url,
            href_pattern=dom.JOB_HREF,
            parser=shape.parse_job_card,
            limit=limit,
            surface="job search",
            allow_empty=True,
        )
        result["query"] = {
            "keywords": keywords.strip(),
            "location": location.strip() or None,
            "remote": remote,
            "date_posted": date_posted,
            "experience_level": levels or None,
            "sort_by": sort_by or "relevance",
            "start": start,
        }
        if not result["results"]:
            result["note"] = (
                "the search page rendered but held no job cards -- either the "
                "filters matched nothing, or the offset is past the end of the "
                "results."
            )
        return result
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_my_profile(include_skills: bool = True) -> dict[str, Any]:
    """Read your own LinkedIn profile as LinkedIn currently stores it.

    Returns name, headline, location, the About text, and which sections are
    present with their item counts.

    On completeness: LinkedIn's own profile-strength meter is not exposed
    here, so this server does not report one. What it reports is derived and
    labelled as such -- which sections rendered and how many entries each
    holds -- so you can see the gaps without a made-up score.

    Args:
        include_skills: also load the full skills page. That is a second page
            load, reported as pages_loaded: 2. Pass false to stay at one.
    """
    try:
        async with BROWSER.session() as page:
            final_url = await BROWSER.goto(page, f"{BASE_URL}/in/me/")
            assert_not_authwall(final_url, surface="profile")
            fields = await dom.read_profile_fields(page)

            if not fields.get("name"):
                raise ExtractionFailedError(
                    "the profile page rendered but no name could be read from "
                    "it, which means the page did not finish loading or "
                    "LinkedIn changed its layout.",
                    url=final_url,
                )

            sections = [s for s in (fields.get("sections") or []) if s]
            out: dict[str, Any] = {
                "name": shape.trim(fields.get("name"), 120),
                "headline": shape.trim(fields.get("headline"), 240),
                "location": shape.trim(fields.get("location"), 120),
                "public_identifier": shape.profile_slug_from(final_url),
                "profile_url": final_url.split("?", 1)[0],
                "about": shape.trim(fields.get("about"), 1200),
                "completeness": {
                    "derived_by": (
                        "this server, from which sections rendered -- not "
                        "LinkedIn's own profile-strength meter"
                    ),
                    "has_photo": bool(fields.get("photo")),
                    "has_about": bool(fields.get("about")),
                    "sections_present": sections,
                    "experience_entries": fields.get("experience_count"),
                    "education_entries": fields.get("education_count"),
                    "skills_listed": fields.get("skills_count"),
                },
                "pages_loaded": 1,
                "source_url": final_url,
            }

            if include_skills:
                slug = out["public_identifier"]
                if slug:
                    skills_url = f"{BASE_URL}/in/{slug}/details/skills/"
                    skills_final = await BROWSER.goto(page, skills_url)
                    assert_not_authwall(skills_final, surface="skills")
                    records = await dom.harvest_block_cards(
                        page, selectors=["main ul li"], max_items=200, max_chars=300
                    )
                    skills: list[str] = []
                    for record in records:
                        lines = shape.content_lines(record.get("text", ""))
                        if not lines:
                            continue
                        name = shape.trim(lines[0], 80)
                        if name and name not in skills:
                            skills.append(name)
                    out["skills"] = skills
                    out["skills_count"] = len(skills)
                    out["pages_loaded"] = 2
                else:
                    out["skills_note"] = (
                        "could not resolve your public profile identifier, so "
                        "the full skills page was not loaded."
                    )
            return out
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_notifications(
    limit: int = NOTIFICATIONS_DEFAULT_LIMIT,
) -> dict[str, Any]:
    """List your LinkedIn notifications as they appear on the notifications page.

    SIDE EFFECT, stated plainly: opening this page clears LinkedIn's unread
    badge, exactly as it would if you opened the page in your own browser.
    That is inherent to loading the page, not something this tool does on
    purpose -- there is no mark-as-read call here, and individual items are
    not opened. It is the only server-side change any tool in this package
    causes, and if you would rather it did not happen, do not call this tool.

    Args:
        limit: maximum notifications to return (default 20, max 50).
    """
    limit = _clamp(limit, NOTIFICATIONS_DEFAULT_LIMIT, NOTIFICATIONS_MAX_LIMIT)
    try:
        async with BROWSER.session() as page:
            final_url = await BROWSER.goto(page, f"{BASE_URL}/notifications/")
            assert_not_authwall(final_url, surface="notifications")
            records = await dom.harvest_block_cards(
                page,
                selectors=dom.NOTIFICATION_SELECTORS,
                max_items=limit * 2,
            )
            dom.require_rows(
                records,
                url=final_url,
                surface="notifications",
                hint=(
                    "notifications is the surface with the least dependable "
                    "markup; if the page clearly has items, the selector list "
                    "in dom.NOTIFICATION_SELECTORS needs updating."
                ),
            )
            rows, dropped = dom.parse_all(records, shape.parse_notification)
            envelope = shape.envelope(
                rows, limit=limit, source_url=final_url, dropped=dropped
            )
            envelope["side_effect"] = (
                "loading this page cleared LinkedIn's unread notification badge"
            )
            return envelope
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_server_info() -> dict[str, Any]:
    """Describe this server: what it can do, what it deliberately cannot.

    Useful for confirming the read-only boundary and the rate settings without
    reading the source.
    """
    try:
        return {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "read_only": True,
            "writes_available": [],
            "capabilities": [
                "profile views (365-day depth where the account has Premium Career)",
                "applied jobs and their status",
                "saved jobs",
                "job search with filters",
                "own profile",
                "notifications",
                "session status",
            ],
            "out_of_scope_by_design": [
                "applying to jobs",
                "saving or unsaving jobs",
                "messaging, InMail, connection invitations",
                "profile edits and Open To Work",
                "posting, liking, commenting, endorsing",
                "marking notifications read",
                "collecting data about other members",
            ],
            "known_side_effects": [
                "opening the notifications page clears the unread badge",
                "running a job search adds to your own recent-search history",
            ],
            "rate_discipline": {
                "min_seconds_between_page_loads": MIN_NAVIGATION_INTERVAL_S,
                "max_page_loads_per_call": MAX_NAVIGATIONS_PER_CALL,
                "auto_paging": False,
                "scheduled_or_background_activity": False,
            },
            "browser": {
                "engine": "playwright chromium, persistent profile",
                "profile_dir": str(CHROME_PROFILE),
                "profile_lock_held_by_pid": held_by(),
                "idle_close_seconds": IDLE_CLOSE_S,
                "detection_evasion": "none -- ordinary automated browser",
            },
        }
    except Exception as exc:
        return _error(exc)


def main() -> None:  # pragma: no cover - process entry point
    logging.basicConfig(level=logging.WARNING)
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
