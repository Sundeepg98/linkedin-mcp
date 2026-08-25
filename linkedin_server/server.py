"""The tool surface: seventeen tools, fourteen of which read LinkedIn.

THE OTHER THREE WRITE, and this paragraph has now been wrong in both
directions. Until 2026-08-23 it read *"There is no write path TO LINKEDIN in
this package"*, which was true and then was not. It was corrected to "sixteen
tools, two writes" -- and stayed there through the arrival of a third, so for
a day it understated the surface it exists to describe. ``linkedin_save_job``,
``linkedin_unsave_job`` and ``linkedin_unfollow_company`` are registered
below. Counts in this docstring are re-measured per wave, not carried.

What remains true, and is what ``readonly.py`` still enforces against this
file:

* Nothing here applies to a job, sends a message, edits the profile, toggles
  Open To Work, follows a company, or marks anything read on purpose.
* The package contains exactly ONE mutating call, in ``writes.perform``,
  admitted by path and function and kind in ``readonly.SANCTIONED_MUTATIONS``.
  A second one anywhere fails ``tests/test_readonly.py``.
* Both write tools perform NOTHING without a single-use token from their own
  preview, and nothing at all unless the process was started with writes
  deliberately enabled.
* ``linkedin_unsave_job`` is registered and refuses: the selector it would
  need has never been measured. See its docstring.

Two documented exceptions on the READ side, and neither of them crosses that
line:

* A SIDE EFFECT rather than an action: opening the notifications page clears
  LinkedIn's unread badge, exactly as it would if the operator opened the
  page himself. It is called out in that tool's docstring because a read that
  changes something has to say so.
* ``linkedin_logout`` writes to LOCAL DISK -- it erases this machine's own
  Chrome cookie jar. It issues no request, so LinkedIn never hears about it
  and the account is untouched; the read-only guarantee is about the
  platform, and that guarantee is intact. It is still the one destructive
  thing here, which is why it performs nothing at all without ``confirm``.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from urllib.parse import urlencode

from fastmcp import FastMCP

from linkedin_server import buildinfo, cdp_bridge, dom, preflight, shape, writes
from linkedin_server.auth import (
    assert_not_authwall,
    check_auth,
    login_via_browser,
    logout,
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
    ME_API,
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
        "A window onto the operator's OWN LinkedIn account, driven by his own "
        "signed-in browser on his own machine. Fourteen of the eighteen "
        "tools read and change nothing. FOUR WRITE: linkedin_save_job, "
        "linkedin_unsave_job, linkedin_unfollow_company and "
        "linkedin_apply_job. Call any of them "
        "without a confirm_token and it performs NOTHING -- it reads the "
        "target live and returns a block for HIM to read; only a token from "
        "that block, used once within two minutes, actually acts. NEVER "
        "CONFIRM ON HIS BEHALF. linkedin_unsave_job currently refuses to act "
        "at all and says why. linkedin_unfollow_company takes the NUMERIC "
        "company id from linkedin_followed_companies, never a name. "
        "ON APPLYING, because it is the thing most often asked for and "
        "because this paragraph said the OPPOSITE until 2026-08-25: this "
        "server CAN now submit an application, to a LinkedIn-hosted posting, "
        "through linkedin_apply_job and only behind the same two-step gate. "
        "Three things about it are worth carrying into any answer you give "
        "him. FIRST, it cannot be taken back, and the honest form of that is "
        "stronger than it sounds: nobody has established that LINKEDIN offers "
        "a withdraw at all -- not that this server lacks one. It has never "
        "been measurable, because measuring it needs an application to exist "
        "and his Applied tab reads zero. SECOND, off-site postings are "
        "reported and NOT driven: about half of all postings apply on the "
        "employer's own applicant-tracking system, and for those "
        "linkedin_job_detail's apply_path names the destination host and the "
        "tool stops. THIRD, it will sometimes refuse a posting that looks "
        "fine, because only a single-screen apply flow has ever been observed "
        "and a multi-step one is refused rather than walked. That is the tool "
        "working, not a gap; it says what it saw. "
        "There is no message, no connection request, no InMail, no profile "
        "edit, and no post -- do not look for them or suggest they exist. "
        "Following a company is sanctioned but not performed: the unfollow "
        "cannot be aimed at what a follow would create. "
        "Start with linkedin_auth_status; if it says false, the operator must "
        "call linkedin_login_browser and sign in himself in the window it "
        "opens -- this server never handles a password. That sign-in is a "
        "ONE-TIME step: it lives in an on-disk Chrome profile and survives "
        "both a server restart and a reboot, and linkedin_session_info says "
        "when it lapses. The highest-signal tool is linkedin_who_viewed_me: "
        "where the account has Premium Career it reaches back 365 days. "
        "Each call "
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

    What comes back, block by block, so a caller is never guessing:

      * credential -- li_at, the one cookie that authenticates here. Its
        name, whether it is there, its expiry, and expiry_source naming which
        route produced that date: the live browser's jar, or the on-disk jar
        read with no browser.
      * supporting -- JSESSIONID, role csrf. Not a second credential: it
        cannot sign anything in, it only governs whether the identity call
        can be made at all. It dies with the browser and a fresh one arrives
        on the next page load, so it having lapsed means nothing on its own.
      * renewal -- silent_renew_available is false here, and why says what
        the four servers in this family were ruled on: there is one
        credential layer, so a linkedin_reauth would be linkedin_login_browser
        wearing a different name and it is deliberately not shipped. It also
        carries session_lapses_at / _in_days: the date past which no silent
        renew can help and you sign in by hand. THAT is the number to compare
        against a sibling server, not credential.expires_at -- a server that
        re-mints its own credential shows hours there while its session holds
        for months. On LinkedIn the two coincide, because nothing here can
        carry the session past the cookie, and session_lapses_source says so.
        uses_browser is null rather than false -- there is no renewal here to
        characterise, and a false would claim one exists and happens to need
        no browser -- while mechanism spells out what recovery actually
        costs: a real window and your own hands, never a background refresh.
      * durability -- where the sign-in is kept and what it survives.

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
async def linkedin_logout(confirm: bool = False) -> dict[str, Any]:
    """End the local LinkedIn session by erasing this profile's cookie jar.

    THE ONE DESTRUCTIVE TOOL IN THIS SERVER, and the most expensive thing it
    can do to you. The sign-in it throws away took a full day to establish,
    and there is no automated way to put it back: linkedin_login_browser
    opens a window and you type into it yourself, exactly as you did the
    first time.

    So confirm is False by default and an unconfirmed call performs NOTHING
    AT ALL -- no file is opened, no file is even stat-ed, no browser starts,
    the profile is not read. It hands back a preview naming the exact files a
    confirmed call would erase, what the sign-in cost, and how you get back
    in. Read that first; nothing about this is reversible afterwards.

    Nothing here reaches LinkedIn. This server stays read-only towards the
    platform: no request goes out, no session is ended on LinkedIn's side,
    your account is untouched, and any other browser signed in to it stays
    signed in. What lapses is purely local -- the cookie jar on this machine.

    A profile another process is using is never touched. If the cross-process
    lock is held, the answer is cleared false naming the holder's PID, because
    erasing a jar out from under a live Chromium is how a profile gets
    corrupted -- which costs the same day this tool is asking about.

    Args:
        confirm: False -- the default -- previews and performs nothing. True
            erases the jar.
    """
    try:
        return logout(CHROME_PROFILE, confirm=bool(confirm))
    except Exception as exc:  # pragma: no cover - logout is written not to
        # Belt to auth.logout's braces. That function catches its own
        # failures and returns them as a reason; if one ever escapes anyway,
        # a destructive tool must still answer rather than raise.
        return _error(exc)


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
    has already spent attention on you. Where the account has Premium
    Career, this list reaches
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
async def linkedin_job_detail(job_id: str) -> dict[str, Any]:
    """Read one job posting in full, including the description and the pay.

    Every list tool here returns CARDS -- title, company, location, link.
    This reads the posting behind one of them, which is where the facts that
    settle a decision actually live: the pay range, LinkedIn's own applicant
    count, the workplace and employment type, the hiring status, and the
    description itself. None of those is on any card.

    One page load, one posting. There is no sweep and no paging.

    A read in both directions: this does not apply to the job, does not save
    it, and has no way to change anything about the posting. Nobody else on
    the page is collected either -- LinkedIn draws a hiring team and a
    "people also viewed" rail beside a job, and neither is read here.

    A field the page did not carry comes back null rather than blank. If the
    page did not render the posting at all the call FAILS instead of
    returning an empty one: LinkedIn serves the document title before the
    body, so a title with nothing behind it is never treated as an answer.

    Args:
        job_id: the numeric job id, or a job url to take it from --
            linkedin_search_jobs and linkedin_saved_jobs both return each.
    """
    try:
        raw = str(job_id or "").strip()
        digits = raw if raw.isdigit() else (shape.job_id_from(raw) or "")
        if not digits.isdigit() or len(digits) < 6:
            return {
                "error": "bad_argument",
                "message": (
                    f"job_id must be a numeric LinkedIn job id or a job url, "
                    f"got {job_id!r}. The id is the long number in a job link, "
                    "e.g. 4600000042 in /jobs/view/4600000042."
                ),
            }

        # Built from the digits alone. Nothing the caller typed reaches the
        # url, which is what lets the allowlist pattern refuse a query string
        # outright rather than having to sanitise one.
        url = f"{BASE_URL}/jobs/view/{digits}"
        async with BROWSER.session() as page:
            final_url = await BROWSER.goto(page, url)
            assert_not_authwall(final_url, surface="job posting")

            identity = await dom.read_job_identity(page)
            detail = shape.parse_job_detail(
                await dom.read_main_text(page),
                company=identity.get("company"),
                document_title=identity.get("document_title"),
            )

            if not shape.job_detail_is_believable(detail):
                raise ExtractionFailedError(
                    "the job page loaded but no posting could be read from it. "
                    "Reporting the fields that did arrive would be worse than "
                    "reporting nothing: LinkedIn sets the document title on the "
                    "server, so a posting that never rendered still has a title, "
                    "and a result carrying one with no body reads as a real job "
                    "with an empty description. Either the page had not finished "
                    "rendering, or the posting is no longer there.",
                    url=final_url,
                    hint="open the url yourself and compare with what this reports",
                )

            out: dict[str, Any] = dict(detail)
            out["job_id"] = digits
            out["company_url"] = identity.get("company_url")
            out["url"] = f"{BASE_URL}/jobs/view/{digits}"

            # Whether this employer is already followed, read off the page that
            # is ALREADY open. No second load, no second surface: the control
            # is on the posting, which is also the only place a follow would
            # ever be performed from, so the state and the action are read from
            # and applied to the same rendering. Three-valued -- see
            # shape.follow_state for why "we could not tell" has to be one of
            # the three.
            control = await dom.read_follow_control(page)
            out["company_follow_state"] = shape.follow_state(
                control.get("label"), count=int(control.get("count") or 0)
            )

            # HOW THIS POSTING IS APPLIED TO, off the same open page and at no
            # extra load. The single most decision-relevant fact a card cannot
            # carry: whether applying happens inside LinkedIn or hands you to
            # somebody else's applicant-tracking system, and if so, WHOSE.
            #
            # A pure READ. LinkedIn draws the apply control as an anchor rather
            # than a button, so the destination is legible without touching it,
            # and the off-site wrapper decodes by string alone -- no redirect is
            # followed and no third-party host is contacted.
            #
            # Three-valued for the same reason every other reader here is, and
            # the third value carries more weight on this one than anywhere
            # else: it feeds the from_state of an IRREVERSIBLE action, so an
            # unidentified route has to be a refusal rather than a default.
            apply_control = await dom.read_apply_control(page)
            out["apply_path"] = shape.apply_route(
                apply_control.get("label"),
                apply_control.get("href"),
                count=int(apply_control.get("count") or 0),
                job_id=digits,
                link_target=apply_control.get("link_target"),
            )

            out["pages_loaded"] = 1
            out["source_url"] = final_url
            return out
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_followed_companies(
    company: str | None = None, limit: int = 50
) -> dict[str, Any]:
    """The company Pages LinkedIn records you as following.

    A read, and the exact counterpart of linkedin_saved_jobs: it answers "is
    this Page already on the list?". This server cannot follow or unfollow
    anything and ships no tool that could.

    THE ONE THING TO READ BEFORE TRUSTING AN ANSWER. LinkedIn draws only the
    first rows of this list and fetches the rest on scroll; this server opens
    one page and reads whatever had drawn. So `complete` is normally false --
    measured 2026-08-23, twenty rows under a heading saying 58 Pages -- and a
    Page missing from `pages` comes back as UNKNOWN, never as not-followed.
    Three-valued on purpose: "absent from the rows I was shown" and "you are
    not following them" are different facts, and reporting the first as the
    second is how a confirm gate ends up pointing the wrong way.

    For a SINGLE employer whose posting you already have, linkedin_job_detail
    is the better read: it reports company_follow_state off the posting page
    itself, at no extra page load, and that answer is never partial.

    Args:
        company: a Page name or numeric Page id to ask about. Leave it out to
            get the whole rendered list.
        limit: how many rows to return.
    """
    try:
        url = f"{BASE_URL}/mynetwork/network-manager/company/"
        async with BROWSER.session() as page:
            final_url = await BROWSER.goto(page, url)
            assert_not_authwall(final_url, surface="followed companies")
            parsed = shape.parse_followed_pages(
                await dom.harvest_followed_pages(page),
                await dom.read_main_text(page),
            )

            # A ZERO IS ONLY REPORTED WHEN LINKEDIN'S OWN COUNT SAYS ZERO.
            # This is `_read_tracker`'s rule applied to a second surface, and
            # it is here because the first version of this tool got it half
            # right: it raised when the heading said a positive number and no
            # row read, but returned a cheerful empty list when the page drew
            # NOTHING AT ALL -- no rows and no heading either. Those are the
            # two failure shapes, not one, and the second is the more likely:
            # a page that never rendered has no count to contradict.
            if not parsed["pages"] and parsed["total_followed"] != 0:
                raise ExtractionFailedError(
                    (
                        "the Manage Pages surface loaded and says you follow "
                        f"{parsed['total_followed']} Pages, but not one row "
                        "could be read from it."
                        if parsed["total_followed"]
                        else "the Manage Pages surface loaded but neither a "
                        "single row NOR its own 'N Pages' heading could be "
                        "read from it, so there is nothing to corroborate a "
                        "zero with."
                    )
                    + " An empty list here would be indistinguishable from you "
                    "following nothing, so it is reported as a failure "
                    "instead.",
                    url=final_url,
                    hint="open the url yourself and compare with what this reports",
                )

            out: dict[str, Any] = {
                "pages": parsed["pages"][:limit],
                "rendered": parsed["rendered"],
                "returned": min(parsed["rendered"], limit),
                "total_followed": parsed["total_followed"],
                "complete": parsed["complete"],
                "pages_loaded": 1,
                "source_url": final_url,
            }
            if parsed["why_incomplete"]:
                out["why_incomplete"] = parsed["why_incomplete"]
            if company:
                out["query"] = company
                out["follow_state"] = shape.followed_page_state(company, parsed)
            return out
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

            # Open To Work, off the topcard lines that were already read.
            # LinkedIn prints the AUDIENCE verbatim next to it ("Open to work
            # <dot> Recruiters only"), and the audience is the half that
            # matters when job-hunting while employed: one setting is
            # invisible to a current employer and the other draws a green frame
            # on the photo for everyone including that employer. Reported as read,
            # never inferred -- on=None means the card did not draw, which is
            # not the same as it being off.
            open_to_work = shape.parse_open_to_work(
                (topcard or {}).get("lines") or []
            )

            slug = shape.profile_slug_from(final_url)
            out: dict[str, Any] = {
                "open_to_work": open_to_work,
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


# ---------------------------------------------------------------------------
# The two writes
# ---------------------------------------------------------------------------
#
# EVERYTHING ABOVE THIS LINE READS. These two do not, and they are the only two
# in the package. Both are two-step by construction: called without a
# ``confirm_token`` they perform NOTHING and return a block for a human to read;
# called with one they redeem it, once, for that action on that target.
#
# They are registered unconditionally rather than hidden behind the flag, and
# that is a deliberate choice against the obvious alternative. A tool that
# appears and disappears with an environment variable is a tool an MCP client
# caches wrongly and a reader discovers by accident; one that is always visible
# and says plainly why it will not act is discoverable and honest. The flag
# still governs BEHAVIOUR -- with it unset these refuse before touching a
# browser -- it just no longer governs visibility.


#: WHY each sanctioned-but-unperformed action is not performed, in one line
#: each. Keyed by action so a new spec that is not performable has to say why
#: here or fail the surface test -- the alternative is a fourth action quietly
#: joining a list of three that a reader takes as complete.
#:
#: Kept SHORT here on purpose. The full reasoning lives in
#: ``writes._refuse_unperformable``, which is what a caller actually hits, and
#: two long copies of one argument drift.
def _irreversible_block() -> dict[str, Any]:
    """What cannot be undone, with a note DERIVED from the lists beside it.

    THE NOTE USED TO BE A HARDCODED STRING and it went false without anyone
    noticing, which is why it is computed now. It read:

        "Every action this process could actually perform is REVERSIBLE ...
         The irreversible one is sanctioned and is NOT performable."

    All four of its clauses were true when written and all four were false the
    moment apply became performable on 2026-08-25 -- while the two LISTS above
    it, which are comprehensions, stayed correct. So the block printed a
    confident reassurance directly beside the accurate data that contradicted
    it, and a reader who trusted the prose over the lists would have been told
    the opposite of the truth about the only action here that cannot be undone.

    Correcting the words would have left the mechanism intact and the next
    drift just as silent. The note is therefore derived from the same
    comprehensions it describes: it cannot now disagree with them, because
    there is nothing left to disagree with.
    """
    performable = sorted(
        spec.action
        for spec in writes.SANCTIONED_WRITES.values()
        if spec.irreversible and spec.action in writes.PERFORMABLE
    )
    sanctioned = sorted(
        spec.action
        for spec in writes.SANCTIONED_WRITES.values()
        if spec.irreversible
    )
    if performable:
        note = (
            f"THIS PROCESS CAN PERFORM {len(performable)} ACTION(S) THAT "
            f"CANNOT BE UNDONE: {', '.join(performable)}. Each is still "
            "two calls behind a single-use token, but the token is the only "
            "thing between a call and a permanent effect -- there is no "
            "inverse to name in the preview, because there is no inverse. "
            "For apply specifically: nobody has established that LinkedIn "
            "offers a withdraw at all, which is a stronger statement than "
            "this server lacking one. See the reversibility field on the "
            "preview block before confirming anything."
        )
    else:
        note = (
            "Every action this process could actually perform is REVERSIBLE, "
            "and its inverse is named in the preview block. Read the two "
            "lists together: the first being empty means something only "
            "because the second is not."
        )
    return {
        "performable_and_irreversible": performable,
        "sanctioned_and_irreversible": sanctioned,
        "note": note,
    }


_WHY_NOT_PERFORMED: dict[str, str] = {
    # apply_job WAS HERE UNTIL 2026-08-25. Its entry read: "the apply FLOW is
    # not measured at all -- no capture of this server's holds a form, a file
    # input, a screening question or a control that submits anything." True
    # when written; the flow was captured on 2026-08-24 and the sentence
    # became false. It is REMOVED rather than reworded, because this dict is
    # for actions that are sanctioned and NOT performed, and apply is now
    # performed. Two halves of that old reason survive where they belong:
    # the off-site refusal moved INSIDE the action, since the route is a
    # per-posting fact rather than a property of the verb, and the
    # irreversibility moved into linkedin_apply_job's docstring, sharpened --
    # nobody has established LinkedIn offers a withdraw at all.
    "follow_company": (
        "an unfollow now exists, but it cannot be aimed at what a follow "
        "creates: a posting names its employer by slug, the unfollow surface "
        "addresses rows by numeric company id, and nothing resolves one to "
        "the other. That surface also renders about 20 rows of 58 with no "
        "pagination."
    ),
    "set_open_to_work": (
        "its editor is not addressed by a url at all -- 237 urls and 37 "
        "payload paths measured across five profile captures, zero of which "
        "reach it. It opens as a modal, and the click that would first show "
        "it is also the first that could change it. This is the one setting "
        "here that a current employer can see."
    ),
}


def _writes_off(action: str) -> dict[str, Any]:
    """The refusal a disabled write returns, with the reason and the remedy."""
    return {
        "error": "writes_disabled",
        "message": (
            f"{action} performs nothing: writes are off in this process. Set "
            f"{writes.WRITES_FLAG}=1 in the server's environment and restart "
            "it. This is per-process and off by default, so a fresh clone of "
            "this repo cannot write to LinkedIn at all."
        ),
        "performed": False,
    }


async def _write_tool(action: str, target: Any, confirm_token: str) -> dict[str, Any]:
    """Preview or perform, for EVERY write tool on this surface.

    ONE implementation, because the writes differ only in their spec and a
    second copy is a second place for the gates to drift apart. ``target`` is
    whatever the spec's ``target_kind`` says it is -- a job id for the save
    pair, a numeric company id for the unfollow -- and it is normalised by
    ``writes._target_for`` rather than here, so a tool cannot accept a shape
    its own action does not address.
    """
    if not writes.writes_enabled():
        return _writes_off(action)
    spec = writes.spec_for_action(action)
    async with BROWSER.session() as page:
        if not str(confirm_token or "").strip():
            return await writes.preview(
                spec, target=target, navigator=BROWSER, page=page
            )
        grant = writes.consume(
            str(confirm_token).strip(),
            action=action,
            target=str(target if target is not None else "").strip(),
        )
        return await writes.perform(BROWSER, page, grant)


@mcp.tool()
async def linkedin_save_job(job_id: str, confirm_token: str = "") -> dict[str, Any]:
    """Bookmark one job posting on LinkedIn. Two steps, and the first is free.

    THIS TOOL CHANGES SOMETHING ON LINKEDIN, which no other tool in this server
    does. It is the reason ``linkedin_server_info`` no longer reports
    ``read_only: true``.

    CALL IT WITHOUT ``confirm_token`` FIRST. Nothing is done: the posting and
    your own saved list are read live, and you get back a block naming the job
    by title and employer, saying which way the toggle would move, where each
    fact was read from, and how the action can be undone. Read it, then call
    again with the ``confirm_token`` it hands you.

    The token works ONCE, only for this posting, only for this verb, and it
    expires in two minutes -- so a scheduled or unattended caller can never
    hold a live one. That is the intended consequence and not a side effect.

    After the click the result is confirmed from a DIFFERENT surface: your
    saved list, with LinkedIn's own per-tab count, rather than from the button
    that was just pressed. ``performed`` comes back ``true``, ``false``, or
    ``"unknown"``; on ``"unknown"`` do not retry, because a retry on a toggle
    that did land performs the opposite action -- look at your saved jobs
    instead.

    Args:
        job_id: the numeric LinkedIn job id, as it appears in /jobs/view/<id>.
        confirm_token: leave empty to preview. Pass the token from that
            preview to actually save.
    """
    try:
        return await _write_tool("save_job", job_id, confirm_token)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_unsave_job(job_id: str, confirm_token: str = "") -> dict[str, Any]:
    """Remove one job posting from your saved list. Built, gated, and refusing.

    Same two-step shape as ``linkedin_save_job`` and the same gates, with ONE
    honest difference that this docstring will not bury: THIS TOOL CANNOT
    PERFORM ANYTHING TODAY, and it is not because the code is missing.

    LinkedIn labels the save control by its accessible name, and the name it
    wears when a posting IS saved has never been observed on this account --
    there has been nothing saved on it to observe. Every capture this repo
    holds shows the unsaved state. So the selector an unsave would click is
    unknown, and this server will not guess one: "Saved" and "Unsave the job"
    are both plausible spellings and it has seen neither.

    THE FIX IS ONE MEASURED LINE, and the first supervised save produces it --
    ``linkedin_save_job`` reads back the label the control changes into and
    reports it. Until that label is written down, this refuses with that
    explanation rather than clicking something it hopes is the right button.

    A preview may also be unrenderable for a second and unrelated reason: an
    unsave is only valid on a posting that is currently saved, so with an empty
    saved list there is nothing to preview it against. The preview says so.

    Args:
        job_id: the numeric LinkedIn job id, as it appears in /jobs/view/<id>.
        confirm_token: leave empty to preview. A token is accepted but the
            action behind it will refuse until its anchor has been measured.
    """
    try:
        return await _write_tool("unsave_job", job_id, confirm_token)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_apply_job(job_id: str, confirm_token: str = "") -> dict[str, Any]:
    """Submit an application to one LinkedIn-hosted job posting.

    THIS ONE CANNOT BE TAKEN BACK, and the usual reassurance is not available
    here, so read the next sentence rather than the shape of it.

    **NOBODY HAS ESTABLISHED THAT LINKEDIN OFFERS A WITHDRAW AT ALL.** That is
    a stronger and worse statement than "this server cannot withdraw it",
    which would invite you to assume LinkedIn can. It might. It has not been
    measured, and it could not be: measuring a withdraw means enumerating the
    controls on an APPLIED row, this account's Applied tab reads zero, and
    getting a row there means applying. So the first application made through
    this tool is the one that settles the question -- and if the answer turns
    out to be no, it will be settled by an application that cannot be undone.

    CALL IT WITHOUT ``confirm_token`` FIRST. Nothing is submitted. The posting
    is read live and you get back a block naming the job by title and
    employer, which of the two apply routes it uses, where that was read from,
    and the exact control that would be pressed. Read it, then call again with
    the token it hands you.

    The token works ONCE, only for this posting, only for this verb, and it
    expires in two minutes, so an unattended caller cannot hold a live one.

    OFF-SITE POSTINGS ARE REPORTED, NOT DRIVEN. About half of all postings
    apply on the employer's own applicant-tracking system rather than on
    LinkedIn. For those this names the destination host and stops. Driving a
    form on somebody else's domain, under their terms, is not this server's to
    do at any capture quality -- ``linkedin_job_detail``'s ``apply_path``
    tells you where to go and you apply there yourself.

    WHAT HAPPENS WHEN YOU CONFIRM, because the shape matters. The apply
    control is opened, which draws LinkedIn's apply form as a modal over the
    posting and submits nothing. The modal is then RE-READ, and the submit is
    only pressed if all of: it rendered; exactly one control carries
    LinkedIn's own submit hook; that control is visible and enabled; its name
    corroborates the hook; and **zero advance controls are present**.

    THAT LAST CONDITION WILL SOMETIMES REFUSE A PERFECTLY GOOD POSTING, and
    that is the tool working rather than a gap. Exactly one apply flow has
    ever been observed on this account -- a single screen with one enabled
    "Submit application" and no Next. A posting that draws a Next is a
    multi-step flow nobody here has watched finish, and filling in steps that
    have never been seen, to reach a submit that cannot be withdrawn, is the
    one guess this server does not make. When that happens it says so and
    names what it saw; apply on the posting yourself.

    Args:
        job_id: the numeric LinkedIn job id, as it appears in /jobs/view/<id>.
        confirm_token: leave empty to preview. Pass the token from that
            preview to actually submit the application.
    """
    try:
        return await _write_tool("apply_job", job_id, confirm_token)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_unfollow_company(
    company_id: str, confirm_token: str = ""
) -> dict[str, Any]:
    """Stop following one company Page. Two steps, and the first is free.

    Same two-step shape and the same five gates as ``linkedin_save_job``. What
    differs is worth reading before you use it, because two of the differences
    change what an answer from this tool means.

    IT IS ADDRESSED BY THE NUMERIC COMPANY ID, NOT BY NAME. Call
    ``linkedin_followed_companies`` first: it prints the id beside each Page.
    A name is refused outright -- names collide, they change, and they belong
    to somebody else -- and the click is anchored to the row carrying the id,
    so the thing you name and the thing that gets pressed are the same row by
    construction. The preview still prints the NAME, because an id is not
    something a person can check.

    THE LIST IS NEVER COMPLETE, AND THAT IS THE IMPORTANT ONE. LinkedIn renders
    about twenty rows of however many you follow, and offers no way to page
    through the rest. So a Page that is not in the rendered rows comes back
    "unknown" rather than "not followed", and the preview refuses rather than
    guessing. If the company you want is not reachable, this tool will say so
    instead of doing nothing quietly.

    Confirmation after the click is read by RELOADING the same list -- there is
    no second surface that lists followed Pages -- and the verdict rests on
    LinkedIn's own stated total dropping by one, not on the row having
    vanished. On a partial list an absent row is not evidence.

    THE PAIR IS ASYMMETRIC ON PURPOSE: this server can stop a follow and cannot
    start one. ``linkedin_follow_company`` is specced and is not performed.

    Args:
        company_id: the numeric LinkedIn company id, as printed by
            ``linkedin_followed_companies``.
        confirm_token: leave empty to preview. Pass the token from that
            preview to actually unfollow.
    """
    try:
        return await _write_tool("unfollow_company", company_id, confirm_token)
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
            # THESE TWO FIELDS WERE LITERALS -- `True` and `[]` -- until
            # 2026-08-23, and they were true for as long as this package had
            # no write path. It has one now, and a server that can write while
            # reporting that it cannot is worse than one that never could: the
            # claim is the thing a caller trusts INSTEAD of reading the source.
            #
            # They are COMPUTED rather than flipped to a new pair of literals,
            # because "this server has a write path" and "this process can
            # perform a write" are different facts and flattening them would
            # be the same error in the other direction. With the flag unset --
            # the default, and the state of a fresh clone -- nothing here can
            # write, and saying otherwise would frighten a reader off a
            # capability he does not have. So:
            #
            #   read_only        -- about THIS PROCESS, right now.
            #   writes_available -- what THIS PROCESS would actually perform.
            #   writes_sanctioned -- what the CODE can ever perform, flag or
            #                        no flag. Never empty, so the capability
            #                        cannot hide behind an unset variable.
            "read_only": not writes.writes_enabled(),
            "writes_available": (
                sorted(writes.PERFORMABLE) if writes.writes_enabled() else []
            ),
            "writes_sanctioned": sorted(writes.PERFORMABLE),
            # A THIRD LAYER, ADDED 2026-08-24, because two fields could not
            # hold three facts. There are actions this server has SPECCED and
            # GATED and will never execute, and before this field they were
            # invisible from here -- so "applying is not offered" and "applying
            # was examined in detail and refused for a measured reason" looked
            # identical to a caller. They are not the same, and the second is
            # the one that tells him what would change it.
            "writes_sanctioned_but_not_performed": {
                spec.action: {
                    "why_not": _WHY_NOT_PERFORMED[spec.action],
                    "has_a_measured_surface": spec.url_template is not None,
                    "can_hold_a_grant": spec.url_template is not None,
                    "irreversible": spec.irreversible,
                }
                for spec in sorted(
                    writes.SANCTIONED_WRITES.values(), key=lambda s: s.action
                )
                if spec.action not in writes.PERFORMABLE
            },
            # IRREVERSIBILITY, REPORTED HERE RATHER THAN ONLY IN A PREVIEW.
            # A confirm block names it for the one action being confirmed, and
            # by then the caller has already decided to try. This answers the
            # question BEFORE that: is there anything here that cannot be
            # taken back?
            #
            # Both lists are computed and BOTH are printed even when one is
            # empty, because "nothing performable is irreversible" is the
            # reassuring half and it means nothing without the other half
            # beside it -- an empty list on its own reads as "we checked" when
            # it could equally mean "we have no such actions to check".
            "irreversible": _irreversible_block(),
            "writes_note": (
                "Every write is two calls: one that performs nothing and "
                "returns a block to read, and one that redeems a single-use "
                "token from it. The token is bound to one action on one "
                "target and expires in "
                f"{writes.GRANT_TTL_SECONDS:.0f}s, which makes an unattended "
                "or scheduled write structurally impossible. Writes are off "
                f"per process unless {writes.WRITES_FLAG} is set; they are "
                f"currently {'ON' if writes.writes_enabled() else 'OFF'}. "
                "unsave_job is sanctioned and gated but REFUSES to act: the "
                "accessible name LinkedIn gives the save control on a saved "
                "posting has never been observed on this account, and this "
                "server will not guess a selector. unfollow_company is "
                "addressed by NUMERIC COMPANY ID, not by name, and refuses "
                "when the Page is not among the rows LinkedIn rendered -- that "
                "surface shows part of the list and offers no way to page "
                "through the rest."
            ),
            # The fields above are about LINKEDIN. ONE tool changes something
            # on THIS MACHINE, and a boundary claim that quietly omitted it
            # would be exactly the kind of claim this server exists in order
            # not to make. So it gets its own named field rather than being
            # folded into a read_only a reader would take as covering
            # everything.
            # ONE REQUEST THIS SERVER MAKES THAT IS NOT A PAGE LOAD, declared
            # 2026-08-24 because until then nothing said it existed.
            #
            # The read boundary is described everywhere in this repo as the
            # door every read goes through. That is precise and slightly
            # narrower than it reads: assert_read_url is the only door to
            # page.goto, and this call is not a navigation, so it never
            # reaches it. Measured: readonly.is_read_url(ME_API) is False --
            # the endpoint this server has always used to answer "am I signed
            # in" would be REFUSED by its own allowlist if that allowlist were
            # consulted.
            #
            # Nothing is wrong with the request. It is one hardcoded constant,
            # GET only, to LinkedIn's own identity endpoint, and no caller can
            # redirect it -- tests/test_api_call_sites.py enumerates every
            # direct HTTP call site in the package by AST and fails if a
            # second one appears or this one moves. What was wrong was that a
            # reader of this block could not have known the path existed.
            # WHAT THE READ BOUNDARY COVERS, said in the block a caller reads
            # rather than left to be inferred from readonly.py's source. The
            # claim there -- "the only door to page.goto" -- is exact and
            # reads as broader than it is, and a reader who takes it for full
            # coverage has understood a different sentence that the true one
            # is easily mistaken for.
            "read_boundary_scope": (
                "NAVIGATION-ONLY. readonly.assert_read_url gates every "
                "page.goto this server performs and nothing else. A request "
                "issued with page.request.get is not a navigation and does "
                "not reach it -- see direct_api_reads below for the one such "
                "request that exists, which is covered by an enumerated "
                "call-site list instead of by a url pattern."
            ),
            "direct_api_reads": [
                f"{ME_API} -- GET, once per auth check, to answer whether "
                "there is a live session. A page load cannot answer that "
                "honestly, which is why this call exists. Issued by auth. It is "
                "NOT covered "
                "by the read allowlist: that allowlist gates navigations, and "
                "this is not one.",
                f"http://127.0.0.1:{CDP_PORT}/json/version -- GET, LOOPBACK "
                "ONLY, issued by cdp_bridge for linkedin_cdp_status. It asks a "
                "Chrome running on "
                "this machine whether it is attachable. It never leaves the "
                "host and reaches no third party. LISTED SECOND HERE FROM "
                "2026-08-24: this field previously presented a complete list "
                "naming only the call above, because the enumerator matched "
                "one call shape and was blind to a bare urlopen. The list was "
                "wrong, not merely short.",
            ],
            "direct_api_reads_note": (
                "Both are GET and neither is gated by the read allowlist, "
                "which covers navigations only -- see read_boundary_scope. "
                "They are covered instead by an enumerated call-site list in "
                "tests/test_api_call_sites.py that hunts BOTH call shapes and "
                "fails if the package grows a third direct request."
            ),
            "local_state_writes": [
                "linkedin_logout(confirm=True) erases this machine's Chrome "
                "cookie jar, which ends the local sign-in. It issues no "
                "request, so LinkedIn is never told and the account is "
                "untouched. Without confirm it performs nothing at all."
            ],
            "capabilities": [
                "profile views (365-day depth where the account has Premium Career)",
                "applied jobs and their status",
                "saved jobs",
                "job search with filters",
                "one job posting in full: pay, applicant count, description",
                "own profile",
                "notifications",
                "session status",
            ],
            # "saving or unsaving jobs" LEFT THIS LIST on 2026-08-23, because
            # it stopped being true and a stale entry here is a lie a caller
            # acts on. Everything still on it is still refused by design, and
            # following a company -- which IS sanctioned in writes.py -- is
            # named explicitly rather than left off, because it is the one
            # thing on this list whose absence a reader might otherwise take
            # as an oversight.
            # REVIEWED IN FULL ON 2026-08-24, when the scope restriction that
            # produced most of this list was lifted and each entry had to
            # re-earn its place. Three kinds of entry now live here and they
            # are NOT the same kind of "no", so they are labelled:
            #
            #   POLICY   -- refused because it should be, whatever gets
            #               measured. These do not expire.
            #   MEASURED -- examined, and refused for a reason somebody took a
            #               reading to establish. These name what would lift
            #               them, and the detail is in
            #               writes_sanctioned_but_not_performed above.
            #   UNMEASURED -- nobody has looked. Kept separate from the other
            #               two, because presenting an unexamined gap as a
            #               design decision is the exact claim this server had
            #               to retract about its own write path.
            #
            # THE UNMEASURED CATEGORY IS CURRENTLY EMPTY, and that is a fact
            # worth reading rather than an omission: as of 2026-08-24 every
            # refusal below has actually been examined. Its last member was
            # inbox reading, which was measured and moved to MEASURED. The
            # label stays defined because the honest thing to do with the next
            # unexamined gap is to add it here rather than to dress it as a
            # decision -- an empty category is cheap, and the alternative is
            # the failure this taxonomy exists to prevent.
            # FOUR FIELDS, NOT ONE, FROM 2026-08-25, and the operator is the
            # reason. He said, of the single list this replaces:
            #
            #   "If something is not technically possible, then refusing it is
            #    a different story. If something is technically possible and
            #    still you are refusing it, I don't know why."
            #
            # He was right, and the old list could not answer him: a wall and a
            # decision sat in the same bucket wearing the same label, so the
            # only way to tell them apart was to go and read the audit
            # documents. That is not a thing a caller should have to do.
            #
            # So the kinds are now SEPARATE KEYS rather than prefixes on one
            # list, because a prefix is easy to skim past and a field name is
            # not. The full classification, with the measurement behind every
            # entry, is _audit/2026-08-25-cannot-vs-will-not.md.
            #
            # APPLYING HIS RULING SHRANK THE POLICY LIST FROM FIVE ENTRIES TO
            # TWO, and that is the substantive change rather than the renaming.
            # Posting, liking, commenting, messaging, InMail, invitations and
            # withdrawing were all filed as POLICY. They are not policy. They
            # are things he might want to do with his own account, refused on
            # somebody else's judgement about his job search -- which is
            # exactly what he objected to. They moved to not_yet_measured,
            # because nobody has looked at any of them.
            #
            # What stayed under policy is the pair that protects SOMEBODY OTHER
            # THAN HIM. That is the whole test, and it is why those two are not
            # his to overrule.

            # Measured, and the measurement shows there is nothing to drive.
            # The only honest permanent refusals, each stating the measurement
            # rather than the decision.
            "cannot_be_done": [
                "MARKING NOTIFICATIONS READ. 34 activatable controls were "
                "enumerated on the notifications surface and not one of them "
                "names read, unread, seen or a badge; the 14 menu items were "
                "fully enumerated and none changes read state; and no "
                "notification carries a per-item id, so there would be nothing "
                "to aim an action at even if a control existed. LinkedIn marks "
                "the list seen SERVER-SIDE when the page is served. There is "
                "no control and no target. AND THE THING YOU ACTUALLY WANT "
                "ALREADY HAPPENS: the badge clears when the page is read, "
                "which linkedin_notifications does. This is not a withheld "
                "feature, it is an automatic one."
            ],

            # Measured POSSIBLE, and not performed anyway. THIS FIELD IS MEANT
            # TO BE EMPTY. Every entry needs a named human reason, and "the
            # server would rather not" is not one -- it is his account. Both
            # entries below are pending wiring, not standing refusals.
            "can_be_done_and_is_refused": [
                # APPLYING LEFT THIS LIST ON 2026-08-25, and that is what the
                # field is for. Its entry named something measured to work
                # that was not being done, and the answer to an entry here is
                # to build it rather than to justify it. linkedin_apply_job
                # now ships, gated, and the list got shorter by one.
                "READING the message inbox. Measured 2026-08-24: it renders, "
                "the conversation list is enumerable, no auth wall. Pending "
                "wiring. The COST is documented rather than hidden: asking for "
                "/messaging/ does not stay on the inbox, LinkedIn redirects it "
                "into one specific conversation thread, so a 'read' opens "
                "somebody's conversation on every call.",
            ],

            # Nobody has looked. Kept apart from both of the above, because an
            # unexamined gap presented as a decision is the exact claim this
            # server had to retract about its own write path -- and filing it
            # as "possible, refused by choice" would be the same error pointing
            # the other way. Each entry names what would settle it. This list
            # is meant to EMPTY, not to sit.
            "not_yet_measured": [
                "SENDING a message or InMail -- no capture of a compose "
                "surface exists. Blocked on measurement, not on choice.",
                "SENDING a connection invitation -- no capture of an invite "
                "control exists either. Both this and InMail need one profile "
                "loaded to measure the control, which touches the policy line "
                "below; the resolution is that a recipient is always supplied "
                "by the caller and never discovered by the server.",
                "SETTING Open To Work. 237 urls and 37 payload paths across "
                "five profile captures, zero of which reach an editor -- but "
                "that proves it is not reachable BY NAVIGATION, not that it "
                "cannot be done. It opens as a modal, and modals open by "
                "clicking. The OTW census already nominates the safe first "
                "click: a Show details control whose action list holds one "
                "Navigate and no ServerRequest. Note this is the one setting "
                "here a current employer can see, which argues for a loud gate "
                "rather than for refusing.",
                "FOLLOWING a company. The obstacle is measured and the "
                "solution is not: a posting names its employer by SLUG, the "
                "follow surface addresses rows by NUMERIC id, and nothing "
                "measured resolves one to the other. Solvable engineering.",
                "EDITING other profile fields. Settle it the same way "
                "Open To Work will be settled, on the same page: load "
                "/in/<his handle>/ and enumerate every control whose "
                "action opens an editor, recording for each whether it "
                "carries a url or only a modal. The OTW census already "
                "did this for one setting; nobody widened it.",
                "CHANGING account settings. /settings/ is on the "
                "forbidden substring list and has never been loaded, so "
                "nothing is known about it -- not which settings are "
                "url-addressed, not which are modal, not which are "
                "visible to anyone else. Settle it by loading the "
                "settings index read-only and enumerating its sections.",
                "WITHDRAWING an application. A real LinkedIn feature, and "
                "the one that would most change how safe applying is -- "
                "an apply that can be undone is a different risk from one "
                "that cannot. Settle it on /jobs-tracker/?stage=applied, "
                "by enumerating the controls on an applied row. Note that "
                "tab currently reads zero, so a measurement needs an "
                "application to exist first.",
                "POSTING or sharing an update. Settle it by enumerating "
                "the composer controls on /feed/, which this server "
                "already loads as a corroborating auth check and has "
                "never read for this purpose.",
                "COMMENTING on a post. Needs one post rendered to "
                "enumerate its comment control. A comment is public and "
                "attributed to him, so if it is ever built the preview "
                "must show the exact text before anything is posted.",
                "LIKING or reacting to a post. Same surface as commenting "
                "and settled by the same capture. Cheaper to build than "
                "commenting because there is no free text to preview, and "
                "it is reversible, which almost nothing else here is.",
                "ENDORSING a member's skill. Never looked for, and it "
                "needs one profile loaded to enumerate the control. This "
                "one WRITES TO A THIRD PARTY'S PROFILE rather than to "
                "his, so the policy line below governs whether it may be "
                "built at all -- that is a different question from "
                "whether it is possible, and it is not settled by "
                "measuring.",
            ],

            # Possible, and refused anyway. TWO ENTRIES, and what they share is
            # the only thing that earns a place here: each protects somebody
            # who is not the operator. That is why these are not his to
            # overrule, and each entry says who it protects.
            "refused_as_policy": [
                "COLLECTING DATA ABOUT OTHER MEMBERS. Protects: the members "
                "whose data it would be. This is the one refusal on this "
                "server that is not the operator's to lift, because the person "
                "it protects is not him. A tool may act on ONE person he "
                "names; it may not discover, search, enumerate or scrape "
                "people.",
                "DRIVING AN OFF-SITE APPLICANT-TRACKING SYSTEM. Protects: the "
                "third party whose form and domain it is. linkedin_job_detail "
                "already reports apply_path and names the destination host, so "
                "a caller learns where the application would go; reporting and "
                "stopping is the behaviour, and it is not a gap.",
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
