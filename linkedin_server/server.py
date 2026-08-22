"""The tool surface: eleven tools, every one of them a read.

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

from linkedin_server import buildinfo, cdp_bridge, dom, preflight, shape
from linkedin_server.auth import (
    assert_not_authwall,
    check_auth,
    login_via_browser,
    session_info,
    session_info_offline,
)
from linkedin_server.browser import BROWSER
from linkedin_server.config import (
    BASE_URL,
    CDP_PORT,
    DEFAULT_LIMIT,
    IDLE_CLOSE_S,
    LAUNCH_ARGS,
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
    REPO_ROOT,
    display,
    scrub,
)
from linkedin_server.errors import ExtractionFailedError, LinkedInReaderError
from linkedin_server.profile_lock import held_by

# ---------------------------------------------------------------------------
# What code this process is running -- resolved ONCE, here, at import
# ---------------------------------------------------------------------------

#: The commit this process was imported from, frozen at import and never
#: re-read. A per-call ``git rev-parse`` from a stale process would report the
#: NEW commit on disk and read as confirmation that a fix is loaded, which is
#: the exact failure this exists to prevent. ``linkedin_server_info`` READS
#: this constant; it must never re-resolve.
BUILD = buildinfo.stamp(REPO_ROOT)

#: When this process came up. Kept OUT of the frozen stamp on purpose: uptime
#: is derived fresh on every call, and a cached uptime is a lie that grows.
CLOCK = buildinfo.ProcessClock()

#: There is NO second stamp to report here. The sibling naukri, uplers and
#: instahyre servers report a ``jobcore`` commit alongside their own because
#: they depend on that library; this server does not depend on it and must not
#: start -- it VENDORS the two modules it needs (see the headers on
#: ``buildinfo.py`` and ``paths.py``). Stated as a value in the payload rather
#: than left as a missing key, because an absent field is indistinguishable
#: from a field nobody remembered to write, and a reader comparing two servers
#: in this family would be left guessing.
JOBCORE_STAMP_NOTE = (
    "none -- this server has no jobcore dependency. It vendors buildinfo.py "
    "and paths.py from jobcore d1720c3 instead; the vendored commit is pinned "
    "in each file's header and tests/test_vendored_buildinfo.py fails if a "
    "copy drifts. Reporting a jobcore stamp here would be a lie."
)


mcp = FastMCP(
    name=SERVER_NAME,
    instructions=(
        "Read-only window onto the operator's OWN LinkedIn account, driven by "
        "his own signed-in browser on his own machine. Every tool reads; none "
        "of them changes anything on LinkedIn. There is no apply, no save, no "
        "message, no connection request, no profile edit -- those are out of "
        "scope by design, so do not look for them or suggest they exist. "
        "Start with linkedin_auth_status; if it says false, the operator must "
        "call linkedin_login_browser and sign in himself in the window it "
        "opens -- this server never handles a password. That sign-in is a "
        "ONE-TIME step: it lives in an on-disk Chrome profile and survives "
        "both a server restart and a reboot, and linkedin_session_info says "
        "when it lapses. The highest-signal tool is linkedin_who_viewed_me: "
        "where the account has Premium Career, so it reaches back 365 days. Each call "
        "loads exactly one page, so ask for one thing at a time rather than "
        "sweeping."
    ),
)


# ---------------------------------------------------------------------------
# Shared plumbing
# ---------------------------------------------------------------------------


def _error(exc: Exception) -> dict[str, Any]:
    """Report a failure as a failure, with everything needed to act on it."""
    if isinstance(exc, LinkedInReaderError):
        out: dict[str, Any] = {"error": exc.kind, "message": scrub(str(exc))}
        url = getattr(exc, "url", "")
        if url:
            out["url"] = url
        hint = getattr(exc, "hint", "")
        if hint:
            out["hint"] = scrub(hint)
        return out
    # An OSError stringifies with the filename it failed on, so this line
    # publishes an absolute path from call sites that render no path field of
    # their own. Every tool funnels its failures through here, which makes this
    # ONE boundary the cheapest place to close that whole class.
    return {
        "error": "unexpected",
        "message": scrub(f"{type(exc).__name__}: {exc}"),
    }


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


async def _read_tracker(
    stage: str, *, tab_label: str, limit: int, surface: str
) -> dict[str, Any]:
    """Read one stage of the job tracker, and say which kind of zero a zero is.

    LinkedIn retired ``/my-items/saved-jobs/`` into ``/jobs-tracker/``, whose
    tabs are client-side radios with no urls of their own; ``?stage=`` is what
    reaches a given list without clicking anything.

    The part that matters is the reconciliation. An empty harvest is ``[]``
    whether the operator has saved nothing or the parser broke, and those two
    must never look alike -- so the tab strip is read as well, and a zero is
    only reported as an empty list when LinkedIn's OWN count for that tab says
    zero and the page drew its empty state. A zero that cannot be corroborated
    that way is a failure and is raised as one.
    """
    url = f"{BASE_URL}/jobs-tracker/?stage={stage}"
    async with BROWSER.session() as page:
        final_url = await BROWSER.goto(page, url)
        assert_not_authwall(final_url, surface=surface)

        main_text = await dom.read_main_text(page)
        tab_counts = shape.parse_tracker_tabs(main_text)
        empty_state = shape.tracker_empty_state(main_text)
        linkedin_count = tab_counts.get(stage)

        records = await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=limit * 3
        )
        rows, dropped = dom.parse_all(records, shape.parse_job_card)

        if not rows and not shape.empty_is_believable(
            linkedin_count=linkedin_count, empty_state=empty_state
        ):
            raise ExtractionFailedError(
                f"no {surface} could be read, and the page does not corroborate "
                f"an empty list: LinkedIn's own {tab_label} tab "
                + (
                    f"says {linkedin_count}"
                    if linkedin_count is not None
                    else "count could not be read"
                )
                + (
                    f", and the empty state ({empty_state!r}) did show"
                    if empty_state
                    else ", and no empty state was drawn"
                )
                + ". Reporting nothing here would be indistinguishable from "
                "you genuinely having none, so it is reported as a failure "
                "instead.",
                url=final_url,
                hint="open the url yourself and compare with what this reports",
            )

        extra: dict[str, Any] = {
            "tab": tab_label,
            "linkedin_count": linkedin_count,
            "tab_counts": tab_counts,
        }
        if not rows:
            extra["empty"] = True
            extra["empty_state"] = empty_state
            extra["note"] = (
                f"EMPTY, and confirmed empty: LinkedIn's own {tab_label} tab "
                f"reads {linkedin_count} and the page drew its empty state "
                f"({empty_state!r}). This is an empty list, not a failed read."
            )
        else:
            extra["empty"] = False
            if linkedin_count is not None and len(rows) > linkedin_count:
                # The mirror of the empty case, and just as much a symptom. A
                # walk that overshoots its row does not return NOTHING, it
                # returns page furniture shaped like a job -- which is how this
                # surface failed in the first place. More rows than LinkedIn
                # counts means something is being read that is not a job.
                extra["note"] = (
                    f"DISAGREEMENT: read {len(rows)} rows but LinkedIn's "
                    f"{tab_label} tab says {linkedin_count}. More rows than the "
                    "page claims usually means something that is not a job is "
                    "being parsed as one, so treat these rows with suspicion "
                    "and open the url yourself."
                )
            elif (
                linkedin_count is not None
                and len(rows) < linkedin_count
                and len(rows) <= limit
            ):
                extra["note"] = (
                    f"read {len(rows)} rows but LinkedIn's {tab_label} tab says "
                    f"{linkedin_count}. This tool loads one page and does not "
                    "scroll, so the rest are below the fold rather than missing."
                )
        return shape.envelope(
            rows,
            limit=limit,
            source_url=final_url,
            dropped=dropped,
            extra=extra,
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


@mcp.tool()
async def linkedin_session_info(verify_live: bool = True) -> dict[str, Any]:
    """Report whether the session is live and how long it has left.

    This is the question that comes up after a week away: is the sign-in still
    good, and when does it lapse? The verdict is the same measured one
    linkedin_auth_status gives -- an authenticated call to the identity
    endpoint, never a cookie's presence -- and alongside it comes the expiry
    date read from the browser profile's own cookie jar.

    The sign-in lives in an on-disk Chrome profile rather than in this
    process, so it survives this server restarting and the machine rebooting.
    What ends it is LinkedIn expiring it, a sign-out, or the profile directory
    going away.

    When no browser can be started at all -- Chromium missing, another process
    holding the profile -- this tool does not die with it. It falls back to
    reading the expiry dates out of that profile's cookie jar on disk, which
    is precisely the moment you most want to know whether the login survived.
    Then 'authenticated' is null and the live_check block says why in plain
    words: a cookie in the jar is not a session, and reporting one as the
    other is a lie this server refuses to tell. Two labelled fields, never one
    blurred one.

    Cookie values are never returned. Only the name, whether it is there, and
    when it lapses. When it has lapsed every read tool says so with a reason
    rather than handing back nothing, and linkedin_login_browser is the way
    back.

    (Everything below this point is dropped from the description a caller
    sees: FastMCP cuts a docstring at Args: and renders the rest into the
    argument schema. Prose that has to reach a caller goes ABOVE it.)

    Args:
        verify_live: put the question to the identity endpoint for a real
            verdict, which requires a working browser. Pass False for the
            free, browserless answer -- jar facts only, 'authenticated' null.
            Default True.
    """
    if not verify_live:
        return session_info_offline(
            CHROME_PROFILE,
            mode=BROWSER.mode,
            why_no_live_check=(
                "not attempted: this call asked for the browserless answer "
                "(verify_live false), so no identity call was made."
            ),
        )
    try:
        async with BROWSER.session() as page:
            return await session_info(page)
    except Exception as exc:
        # The browser is the thing that broke, so the jar is read straight
        # off disk instead. The verdict is NOT downgraded to "a cookie is
        # there" -- it goes to null, and the reason travels with it.
        return session_info_offline(
            CHROME_PROFILE,
            mode=BROWSER.mode,
            attempted=True,
            why_no_live_check=(
                f"no browser could be started, so the identity call could not "
                f"be made: {_error(exc)['message']}"
            ),
        )


@mcp.tool()
async def linkedin_cdp_status() -> dict[str, Any]:
    """Is there a browser this server could attach to? A recovery diagnostic.

    NOT the normal way to run this server, and not something to reach for
    first. The daily path is the persistent Chrome profile: sign in once and
    it holds for as long as LinkedIn honours it. This exists for the day that
    profile's session dies and an automated sign-in is being refused -- then
    the operator can run his own Chrome with a DevTools port open and let this
    server read through that instead.

    It needs a Chrome that is ALREADY RUNNING and that was started with
    --remote-debugging-port. A browser opened from the taskbar has no such
    port, so "my browser is open" is not enough. Worse, when a Chrome is
    already running, a second one started with the flag silently hands its
    arguments to the first and no port opens at all -- so either quit Chrome
    completely first, or give the new one its own --user-data-dir.

    This touches nothing on LinkedIn. It asks the local port what is there and
    reports the answer, or the exact command to run when nothing answered.
    """
    try:
        result = await cdp_bridge.probe()
        result["is_the_daily_path"] = False
        result["active_browser_mode"] = BROWSER.mode
        result["how_to_use"] = (
            "start this server with LINKEDIN_CDP_ATTACH=1 to read through "
            "the attached browser instead of the persistent profile. The "
            "read-only boundary is identical in both modes."
        )
        return result
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

    Viewers browsing with limited visibility appear exactly as LinkedIn shows
    them to you and no more: "Someone at Acme", "Recruiter at Acme", with a
    date and no link, flagged "anonymous": true. They are the majority of a
    typical list and often the most useful part of it -- a recruiter's view
    is a recruiter's view whether or not it comes with a name. This server
    makes no attempt to work out who they are, and there is no code here that
    could: nothing is fetched about any viewer, and no viewer's profile is
    ever opened. What you get is the row LinkedIn already put on your screen.

    Reads the Premium analytics page. The older /me/profile-views/ address
    now redirects to that same page, so the second attempt is a re-load for a
    page that had not finished rendering rather than a different surface; it
    still reports pages_loaded: 2 when it happens.

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
                    page,
                    href_pattern=dom.PERSON_HREF,
                    max_items=limit * 3,
                    # Anonymous viewers carry no link, so a link-anchored
                    # harvest cannot see them at all. Without this the list
                    # is silently shorter than the page it was read from.
                    sibling_rows=True,
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

    Reads the Applied tab of your own job tracker (the page My Items > Applied
    became). Each row carries title, company, location, the status LinkedIn
    shows (applied, application viewed, resume downloaded, no longer accepting
    applications) and how long ago, plus the job id and link.

    Status is whatever LinkedIn displays; this server does not infer, score or
    chase anything, and it cannot see applications you made anywhere else.

    An empty result says so explicitly and carries LinkedIn's own count for the
    tab, so "you have applied to nothing" and "this could not be read" are
    never the same answer. If the two disagree -- no rows, but a non-zero count
    -- you get an error rather than an empty list.

    Args:
        limit: maximum rows to return (default 25, max 100).
    """
    limit = _clamp(limit, DEFAULT_LIMIT, MAX_LIMIT)
    try:
        return await _read_tracker(
            "applied",
            tab_label="Applied",
            limit=limit,
            surface="applied jobs",
        )
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_saved_jobs(limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """List the jobs you have bookmarked on LinkedIn.

    Reads the Saved tab of your own job tracker: title, company, location, when
    it was posted where LinkedIn shows it, and the job link.

    Read-only in both directions -- this lists what you saved and has no way
    to add to or remove from the list.

    An empty result says so explicitly and carries LinkedIn's own count for the
    tab, so an empty list can never be mistaken for a read that failed.

    The tracker also holds In Progress, Interview and Archived tabs. They are
    not exposed as tools: this reads the two lists it names and nothing else.

    Args:
        limit: maximum rows to return (default 25, max 100).
    """
    limit = _clamp(limit, DEFAULT_LIMIT, MAX_LIMIT)
    try:
        return await _read_tracker(
            "saved",
            tab_label="Saved",
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

    Returns name, headline, location, the About text, and which sections were
    on the page when it was read.

    On completeness: LinkedIn's own profile-strength meter is not exposed
    here, so this server does not report one. What it reports is derived and
    labelled as such.

    One honest limitation, stated because its absence would otherwise read as
    data: LinkedIn now defers Experience, Education and Skills until the page
    is SCROLLED, and this server does not scroll. Those sections are therefore
    usually absent from the render, and absent means UNKNOWN here, never zero.
    sections_not_rendered names them, and details_urls gives you the page for
    each one if you want to look yourself.

    Args:
        include_skills: also load the full skills page, which is where a real
            skills list can be read. That is a second page load, reported as
            pages_loaded: 2. Pass false to stay at one.
    """
    try:
        async with BROWSER.session() as page:
            final_url = await BROWSER.goto(page, f"{BASE_URL}/in/me/")
            assert_not_authwall(final_url, surface="profile")
            fields = await dom.read_profile_fields(page)

            sections = [s for s in (fields.get("sections") or []) if s]
            topcard = shape.pick_topcard(sections, fields.get("title"))
            identity = shape.parse_profile_topcard(
                (topcard or {}).get("lines") or []
            )

            if not identity.get("name"):
                raise ExtractionFailedError(
                    "the profile page rendered but no name could be read from "
                    "it, which means the page did not finish loading or "
                    "LinkedIn changed its layout again. The page carries no "
                    "h1 at all now, so the name is taken from the first "
                    "heading inside main, cross-checked against the document "
                    "title.",
                    url=final_url,
                    hint=f"headings seen: {[s.get('heading') for s in sections]}",
                )

            about_lines = shape.profile_section_lines(sections, "About")
            about = shape.trim(" ".join(about_lines), 1200) if about_lines else None

            headings = [str(s.get("heading", "")).strip() for s in sections]
            folded = {h.casefold() for h in headings}
            present = [
                h for h in shape.PROFILE_SECTION_HEADINGS if h.casefold() in folded
            ]
            deferred = [
                h
                for h in ("About", "Experience", "Education", "Skills")
                if h.casefold() not in folded
            ]
            # A section that did not render says nothing about whether it is
            # filled in, so has_about is False only when the About section WAS
            # on the page and held nothing.
            has_about = bool(about) if "about" in folded else None

            slug = shape.profile_slug_from(final_url)
            out: dict[str, Any] = {
                "name": identity["name"],
                "headline": identity["headline"],
                "location": identity["location"],
                "public_identifier": slug,
                "profile_url": final_url.split("?", 1)[0],
                "about": about,
                "completeness": {
                    "derived_by": (
                        "this server, from which sections rendered -- not "
                        "LinkedIn's own profile-strength meter"
                    ),
                    "has_photo": bool((topcard or {}).get("images")),
                    "has_about": has_about,
                    "sections_present": present,
                    "sections_not_rendered": deferred,
                    "headings_seen": headings,
                    "experience_entries": None,
                    "education_entries": None,
                    "skills_listed": None,
                },
                "pages_loaded": 1,
                "source_url": final_url,
            }
            if deferred:
                out["completeness"]["not_rendered_means"] = (
                    "UNKNOWN, not zero. LinkedIn loads these sections only "
                    "once the page is scrolled and this server does not "
                    "scroll, so their absence here says nothing about whether "
                    "they are filled in."
                )
            if slug:
                out["details_urls"] = {
                    section.lower(): f"{BASE_URL}/in/{slug}/details/{section.lower()}/"
                    for section in ("Experience", "Education", "Skills")
                }

            if include_skills:
                if slug:
                    skills_url = f"{BASE_URL}/in/{slug}/details/skills/"
                    skills_final = await BROWSER.goto(page, skills_url)
                    assert_not_authwall(skills_final, surface="skills")
                    records = await dom.harvest_linked_cards(
                        page,
                        href_pattern=dom.SKILL_HREF,
                        max_items=200,
                        max_chars=300,
                    )
                    skills: list[str] = []
                    for record in records:
                        lines = shape.content_lines(record.get("text", ""))
                        if not lines:
                            continue
                        name = shape.trim(lines[0], 80)
                        if name and name not in skills:
                            skills.append(name)
                    out["pages_loaded"] = 2
                    if skills:
                        out["skills"] = skills
                        out["skills_count"] = len(skills)
                        out["completeness"]["skills_listed"] = len(skills)
                        # Say where the number came from. Skills is one of the
                        # sections the profile page defers, so it is listed as
                        # not rendered there AND counted here, and without this
                        # the two read as a contradiction.
                        out["completeness"]["skills_listed_source"] = (
                            "the /details/skills/ page, loaded as the second "
                            "page of this call -- not the profile page, where "
                            "the skills section had not rendered"
                        )
                    else:
                        out["skills_note"] = (
                            "the skills page loaded but no skill entries could "
                            "be read from it. That is a failed read, not an "
                            "empty skills list, so no list is reported."
                        )
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

    ====================== SIDE EFFECT -- READ FIRST ======================
    THIS TOOL CHANGES SOMETHING ON LINKEDIN. Loading the notifications page
    CLEARS YOUR UNREAD BADGE -- every notification LinkedIn was still counting
    as unread stops being counted, exactly as if you had opened the page
    yourself. MEASURED, not theorised: one call on 2026-08-21 took the badge
    from 1 to 0, and it does not come back.

    It cannot be avoided. LinkedIn marks the list seen on the server when the
    page is served, so there is no read of this surface that leaves the badge
    alone: no click, no scroll and no per-item open is involved, and there is
    no mark-as-read call anywhere in this package. The only way not to clear
    the badge is not to call this tool.

    It is the ONE server-side change any tool here causes. Everything else in
    this package leaves LinkedIn exactly as it found it.

    Partial compensation, since the badge is going either way: each row carries
    "unread": true/false as LinkedIn had it AT THE MOMENT OF READING -- which
    is the fact the page load is about to destroy. Read it here or lose it.
    =========================================================================

    Rows carry the notification text, how long ago it arrived, whether it was
    unread, and the link LinkedIn attaches. Screen-reader-only text ("Unread
    notification.", "Status is reachable") is stripped, so the body is what you
    would read on screen.

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
                hidden_selector=dom.NOTIFICATION_HIDDEN_SELECTOR,
                time_selector=dom.NOTIFICATION_TIME_SELECTOR,
                unread_class=dom.NOTIFICATION_UNREAD_CLASS,
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
                "loading this page cleared LinkedIn's unread notification "
                "badge. Unavoidable -- LinkedIn marks the list seen when it "
                "serves the page -- and it is the only change any tool in this "
                "package makes. The per-row 'unread' flag is how it stood "
                "before this call."
            )
            unread = [row for row in envelope["results"] if row.get("unread")]
            envelope["unread_when_read"] = len(unread)
            return envelope
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_server_info() -> dict[str, Any]:
    """Describe this server: what it can do, what it deliberately cannot.

    Useful for confirming the read-only boundary and the rate settings without
    reading the source.

    ``version`` and ``build.code.commit`` are two different facts and both are
    reported. ``version`` is a HAND-MAINTAINED label: it says what this server
    calls itself, and it keeps saying it whether or not anybody remembered to
    bump it. ``build.code.commit`` is MEASURED -- it is the commit this process
    was imported from, read once at import and frozen.

    WHAT TO DO WITH IT. A fix committed to disk changes nothing for a server
    that is already running. To tell "the fix is not loaded" from "the fix is
    wrong", compare ``build.code.commit`` against ``git rev-parse HEAD`` in the
    checkout::

        git -C <this checkout> rev-parse --short=12 HEAD

    They MATCH -> the running process holds that commit, so a bug you can still
    reproduce is a real bug. They DIFFER -> the process is STALE and no further
    committing will change its behaviour until the MCP client restarts it.
    ``build.code.dirty`` says whether the working tree had uncommitted changes
    when this process started, so a matching commit with ``dirty: true`` means
    the commit is necessary but not sufficient to describe what is loaded.
    ``build.process.started_at`` dates the answer.
    """
    try:
        return {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            # Read from module constants; never re-resolved here. A per-call
            # git from a STALE process would report the NEW commit on disk and
            # read as confirmation that a fix is loaded -- worse than silence.
            "build": {
                "code": BUILD.as_dict(),
                "process": CLOCK.as_dict(),
                "jobcore": JOBCORE_STAMP_NOTE,
            },
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
                # Relativised, not deleted: "where does my session actually
                # live" is a real question, and a null answers nothing.
                "profile_dir": display(CHROME_PROFILE),
                "profile_lock_held_by_pid": held_by(),
                "idle_close_seconds": IDLE_CLOSE_S,
                "mode": BROWSER.mode,
                "headless": BROWSER.headless,
                "session_survives_restart_and_reboot": True,
                # Answers "is there a browser to launch at all" WITHOUT
                # launching one, so a broken install is diagnosable from the
                # one tool that still works when every other tool is dying at
                # browser launch. Carries the resolved path and the value of
                # PLAYWRIGHT_BROWSERS_PATH, which is the pair that decides
                # whether the fix is a config line or a download.
                "preflight": await preflight.report(
                    headless=BROWSER.headless, playwright=BROWSER.playwright
                ),
            },
            # Declared as fields rather than prose so it can be asserted on.
            # One flag is passed that touches automation visibility, it is
            # named, and every other technique is enumerated and false.
            "automation_posture": {
                "launch_args": list(LAUNCH_ARGS),
                "navigator_webdriver_disabled": True,
                "stealth_plugin": False,
                "user_agent_spoofing": False,
                "platform_or_timezone_spoofing": False,
                "fingerprint_spoofing": False,
                "proxy": False,
                "randomised_or_humanised_timing": False,
                "mouse_movement_simulation": False,
                "captcha_solving": False,
                "summary": (
                    "one flag, --disable-blink-features=AutomationControlled, "
                    "which stops Blink setting navigator.webdriver to true. "
                    "LinkedIn checks that at sign-in. Everything else on this "
                    "list is false and there is no code in the package that "
                    "could make it true."
                ),
            },
            "recovery_path": {
                "what": "attach to a Chrome the operator started himself",
                "when": "the profile session has died and sign-in is refused",
                "is_the_daily_path": False,
                "enable_with": "LINKEDIN_CDP_ATTACH=1",
                "requires": f"a running Chrome started with --remote-debugging-port={CDP_PORT}",
                "check_with": "linkedin_cdp_status",
            },
        }
    except Exception as exc:
        return _error(exc)


def main() -> None:  # pragma: no cover - process entry point
    logging.basicConfig(level=logging.WARNING)
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
