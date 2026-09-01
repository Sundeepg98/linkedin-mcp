"""The tool surface: thirty-three tools, eight of which write to LinkedIn.

THIS PARAGRAPH HAS NOW BEEN WRONG FIVE TIMES, in both directions, and the
count is the part that keeps rotting. Until 2026-08-23 it read *"There is no
write path TO LINKEDIN in this package"* -- true, then not. It was corrected
to "sixteen tools, two writes", stayed there through the arrival of a third,
and then said "seventeen tools, fourteen reads, THE OTHER THREE WRITE" while
the live surface was twenty and four. It then said "twenty tools, four of
which write" while the live surface was THIRTY-ONE and FIVE, which is the
fourth time.

THE FIFTH IS THE CHEAPEST AND IS RECORDED ANYWAY, because a number that rots
by one is the number a reader stops checking. It said "thirty-one tools ...
NINETEEN read" for as long as it took ``linkedin_profile_editor_fields`` to
arrive later the same day, 2026-08-31. One READ was added and no write was;
the correction is thirty-one -> thirty-two and nineteen -> twenty.

THE SIXTH IS THE SAME SHAPE AS THE FIFTH, ON THE SAME DAY, and it is written
out rather than folded into the paragraph above because two corrections of
the same kind in one day is the evidence that this docstring's numbers are
the part to distrust. ``linkedin_my_activity_items`` arrived after the fifth
correction had been made: another READ, no write, thirty-two -> thirty-three
and twenty -> twenty-one.

THE SEVENTH IS THE ONE WORTH READING, 2026-09-01, because it is not another
tool arriving -- it is this paragraph being WRONG ABOUT ITSELF. It said "THE
NUMBERS ABOVE ARE DERIVED, not counted by hand", and that sentence was false
when it was written. Nothing compared these words against the code. What was
pinned was the INSTRUCTIONS string, by
``test_the_instructions_announce_every_write``, which derives its number from
``writes.PERFORMABLE`` and would fail the moment a write shipped unannounced
-- and it did exactly that job when ``update_setting`` shipped on 2026-08-31,
so the instructions said SIX that day. This docstring kept saying FIVE for a
day and a half, and the reason nobody caught it is the reason it is worth
recording: A CHECK THAT COULD NOT FAIL IS INDISTINGUISHABLE FROM ONE THAT HAS
NOT FAILED YET, and a claim of being checked is worth less than nothing when
it is the thing stopping somebody from checking.

THE NUMBERS ABOVE ARE DERIVED NOW, and that is a statement about a test rather
than about an intention. Thirty-three is ``len(await mcp.list_tools())``,
pinned in ``test_server_surface.py`` by
``test_the_surface_is_exactly_the_thirtythree_tools``; the split is pinned in
the same file by ``test_this_modules_docstring_numbers_are_derived``, which
reads THESE WORDS and fails if any of the three disagrees with the registry.
The surface splits three ways and the split is the part a reader actually
needs: TWENTY-ONE read, EIGHT write, and FOUR are write-shaped, registered, gated
and cannot act at all -- none is in ``writes.PERFORMABLE``, none holds a
``url_template``, and ``writes.mint`` refuses each of them a grant at issue,
so no confirm token for any of them can exist. Twenty-one plus eight plus four is
thirty-three.

NOTE THE SEVENTH ACTION THAT HAS NO TOOL. ``writes.SANCTIONED_WRITES`` holds
THIRTEEN actions where this surface registers TWELVE write-shaped tools, and
the missing one is ``set_open_to_work``: it is sanctioned, it is refused by
``_refuse_unperformable``, and no tool was ever registered for it. So six plus
six counts TOOLS and thirteen counts ACTIONS, and a reader comparing the two
numbers is not looking at a discrepancy.

THE LINE NUMBERS THAT USED TO BE HERE ARE GONE, and that is part of this
correction rather than tidying. It read "pinned at ``test_server_surface.py``
line 356 ... pinned at line 1252 ... pinned at line 413", and all three were
wrong by the time this paragraph was next read: the assertions moved when the
comments above them grew. A citation that rots faster than the claim it
supports is worse than no citation, so the pins are named by TEST NAME, which
a grep finds and an edit does not silently move.

It carried the sentence *"Counts in this docstring are re-measured per wave,
not carried"* through every one of those. A docstring that states its own
discipline and then breaks it is worse than one that never claimed the
discipline, because a reader trusts it more. **The counts here are prose and
nothing tests them** -- ``tests/test_server_surface.py`` pins the real
numbers, and that file is the one to believe when the two disagree.

The eight writes are ``linkedin_save_job``, ``linkedin_unsave_job``,
``linkedin_unfollow_company``, ``linkedin_apply_job``,
``linkedin_follow_company``, ``linkedin_update_setting``,
``linkedin_react_to_item`` and ``linkedin_send_invitation``, all registered
below and all behind the same two-call gate. The last is the first write here
that reaches ANOTHER PERSON, and the first that cannot confirm its own
outcome -- both facts are printed in its confirm block rather than left in
this docstring, where only somebody reading source would meet them. This sentence named FOUR of them
and omitted ``linkedin_follow_company`` until 2026-08-31; it is corrected here
rather than quietly widened, because the omitted name is the one whose absence
made the count wrong. ``linkedin_update_setting`` joined it later that day,
and it is the first write here that acts on neither a job nor a company Page:
it moves ONE named account setting -- dark mode -- on a page measured six
times, by clicking the radio named for the destination.

What remains true, and is what ``readonly.py`` still enforces against this
file:

* Nothing here sends a message, edits the profile, toggles Open To Work, or
  marks anything read on purpose. THIS CLAUSE ALSO READ "follows a company"
  until 2026-08-31 and that word is struck rather than the list quietly
  reworded: ``linkedin_follow_company`` is the FIFTH performable write and
  has been since 2026-08-30, so the sentence was asserting the absence of a
  tool registered below it. The rest of the list still holds, and holds for a
  reason worth stating: message, profile-edit and Open To Work all have
  REGISTERED tools now, and every one of them refuses -- being named here is
  a claim about what can be PERFORMED, not about what appears on the surface.
* The package contains exactly ONE mutating call, in ``writes.perform``,
  admitted by path and function and kind in ``readonly.SANCTIONED_MUTATIONS``.
  A second one anywhere fails ``tests/test_readonly.py``.
* EVERY write tool performs NOTHING without a single-use token from its own
  preview, and nothing at all unless the process was started with writes
  deliberately enabled. (This said "Both write tools" while there were four
  of them -- the same carried-count rot as the headline.)
* ``linkedin_unsave_job`` is registered and PERFORMABLE since 2026-08-30. It
  refused for a month because the selector it would need had never been
  measured; the operator's first save produced that label and a read-only
  route re-measured it three times. It still refuses from any state it does
  not recognise. See its docstring.

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
import re
from typing import Any, Optional
from urllib.parse import parse_qs, urlencode, urlsplit

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
    FEED_URL,
    MESSAGING_URL,
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
        "signed-in browser on his own machine. Most tools read and change "
        "nothing. EIGHT WRITE: linkedin_save_job, "
        "linkedin_unsave_job, linkedin_unfollow_company, "
        "linkedin_follow_company, linkedin_apply_job, "
        "linkedin_update_setting, linkedin_react_to_item and "
        "linkedin_send_invitation. Call any of them "
        "without a confirm_token and it performs NOTHING -- it reads the "
        "target live and returns a block for HIM to read; only a token from "
        "that block, used once within two minutes, actually acts. NEVER "
        "CONFIRM ON HIS BEHALF. linkedin_unfollow_company takes the NUMERIC "
        "company id from linkedin_followed_companies, never a name. "
        "ON UNSAVING, and this paragraph said the OPPOSITE until 2026-08-30 "
        "-- it read 'linkedin_unsave_job currently refuses to act at all and "
        "says why.' It refused because the accessible name LinkedIn gives the "
        "save control on a saved posting had never been observed: he had "
        "nothing saved to observe it on. He saved a posting that evening, the "
        "label was measured four times across two independent routes, and it "
        "is now in the table. So the anchor exists and the click is real. "
        "TWO THINGS TO CARRY INTO ANY ANSWER. FIRST, it is still gated "
        "exactly like the others -- no token, no action -- and an unsave is "
        "not free to him: it drops a posting he chose to keep, and this "
        "server cannot tell him what was in the list before. SECOND, it can "
        "still refuse, and the refusal is now narrow rather than total: it "
        "acts only from a state it RECOGNISES, so a posting whose control it "
        "cannot read is refused rather than clicked. "
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
        "THE SEVEN THAT REFUSE, and this paragraph said the OPPOSITE until "
        "2026-08-30 -- it read 'There is no message, no connection request, "
        "no InMail, no profile edit, and no post -- do not look for them or "
        "suggest they exist.' Every one of those now EXISTS as a tool: "
        "linkedin_publish_post, linkedin_comment_on_item, "
        "linkedin_react_to_item, linkedin_update_profile_field, "
        "linkedin_update_setting, linkedin_send_invitation and "
        "linkedin_send_message. NONE OF THEM CAN ACT. Each reads the relevant "
        "surface live, then refuses and names what it saw, what is missing, "
        "and the one measurement that would complete it -- and no confirm "
        "token is ever issued for any of them, so there is nothing to "
        "confirm. Answer questions about them from what the tool itself "
        "returns rather than from a stored belief: the reason they are the "
        "opposite of a silence is that a silence conflates 'this server will "
        "not' with 'LinkedIn cannot'. Two of them are worth knowing in "
        "advance. linkedin_send_message DOES NOT OPEN MESSAGING -- loading it "
        "is measured to redirect into a stranger's conversation, so the "
        "preview reads the nav badge and stops; if the surface must be "
        "measured, HE calls linkedin_open_messaging, which pays that cost "
        "knowingly. And linkedin_send_invitation DOES NOT OPEN /mynetwork/, "
        "because that load spends his pending-invitation badge; it reads the "
        "invitation controls on his own profile instead. "
        "Following a company IS now performed, through "
        "linkedin_follow_company and behind the same gate -- with one "
        "asymmetry to carry into any answer: this server can start a follow "
        "and cannot aim its own unfollow at what a follow creates, because a "
        "posting names its employer by SLUG and the unfollow surface "
        "addresses rows by NUMERIC ID. Reversible in LinkedIn, by hand; not "
        "by this server. "
        "Endorsing a skill is IMPOSSIBLE AS SPECIFIED and is the one "
        "capability with no tool: zero endorse controls across 13 fixtures "
        "and across 222 controls read live on his own profile, and the only "
        "surface that would carry one is a third party's profile, which this "
        "server may not load for a measurement. "
        "Start with linkedin_auth_status; if it says false, the operator must "
        "call linkedin_login and sign in himself in the window it "
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

        # THE READINESS WAIT RUNS FIRST, AND THE ORDER IS THE WHOLE OF ITS
        # VALUE -- the same argument that put dom.wait_for_job_description at
        # the top of dom.read_job_posting. After the text has been read and the
        # cards harvested, waiting for the list changes nothing about what was
        # read; it would spend up to ten seconds to produce a field describing
        # a page that had already been parsed. Every read below therefore
        # happens on a page that has either resolved its list or spent the
        # bound failing to, and list_wait says which.
        list_wait = await dom.wait_for_tracker_list(page)

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
                "instead. "
                # THE EVIDENCE IS READ HERE AND NOWHERE ELSE -- on the branch
                # that is about to refuse, exactly as the save diagnostic is.
                # A read that succeeded has no use for it, and spending two
                # extra locator calls on every healthy tab to print a field
                # nobody reads is how a diagnostic becomes a tax.
                + shape.tracker_read_note(
                    await dom.read_tracker_evidence(page),
                    list_wait,
                    BROWSER.last_settle,
                    # THE TWO NUMBERS THE CALLER ALREADY HELD AND WAS THROWING
                    # AWAY. The note used to say "the card walk or the row
                    # parser" and could not choose between them; these are what
                    # chooses. records is what the walk built, dropped is what
                    # the parser then rejected.
                    records=len(records),
                    dropped=dropped,
                    census=await dom.harvest_census(
                        page, href_pattern=dom.JOB_HREF, max_items=limit * 3
                    ),
                    row_shape=await dom.read_tracker_row_shape(page),
                    # WHAT THE PARSER ACTUALLY RECEIVED. The refusal could
                    # say the parser rejected the record and not WHICH of
                    # its two None-returns fired, which is where this
                    # investigation stalled. Counts and labels, never lines.
                    traces=[
                        shape.parse_job_card_trace(rec) for rec in records[:3]
                    ],
                ),
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
async def linkedin_login(wait_seconds: int = LOGIN_WAIT_S) -> dict[str, Any]:
    """Sign in to LinkedIn. A browser opens and YOU type; nothing is automated.

    THE CANONICAL NAME, from 2026-08-25. Its sibling servers in this family
    spell it ``naukri_login``, ``instahyre_login`` and ``uplers_login``, and
    this one spelled it ``linkedin_login_browser`` -- the odd name out. That is
    a papercut for somebody who has met the others and a wall for a stranger
    who clones this repository and reaches for the name every other server
    uses. ``linkedin_login_browser`` still works and is now an alias.

    This server never sees, types, stores or transmits a password. It opens a
    browser window at linkedin.com/login; you type into that window; the
    persistent Chrome profile keeps the session afterwards, so this is a
    one-time step until LinkedIn expires it.

    The window stays open until the identity endpoint confirms a real session,
    the window is closed, or wait_seconds runs out. A cookie appearing does
    not end the wait -- it only causes the endpoint to be asked again. On
    timeout the result is authenticated false with a reason, never an
    optimistic success.

    THERE IS NO REAUTH HERE, and that is deliberate rather than missing.
    LinkedIn issues this server no refresh token, so a ``linkedin_reauth``
    would be this tool wearing a different name. ``linkedin_session_info``
    reports that absence as a field rather than leaving a caller to infer it
    from a tool that is not there.

    Args:
        wait_seconds: how long to leave the window open for you. Default 300.
    """
    try:
        async with BROWSER.session() as page:
            return await login_via_browser(page, wait_seconds=int(wait_seconds))
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_login_browser(wait_seconds: int = LOGIN_WAIT_S) -> dict[str, Any]:
    """DEPRECATED ALIAS. Call ``linkedin_login`` instead; this forwards to it.

    Kept working because things already call it, and removing a name that
    used to work is a worse failure than carrying one. It behaves identically
    -- same browser window, same one-time sign-in, same never-handles-a-
    password property -- and there is no plan to remove it.

    The canonical name is ``linkedin_login``, which is what the other three
    servers in this family are called.

    Args:
        wait_seconds: how long to leave the window open for you. Default 300.
    """
    return await linkedin_login(wait_seconds=wait_seconds)


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
        credential layer, so a linkedin_reauth would be linkedin_login
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
    rather than handing back nothing, and linkedin_login is the way
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
    and there is no automated way to put it back: linkedin_login
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
async def linkedin_draft_applications(limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """List the job applications you STARTED on LinkedIn and never sent.

    Reads the In Progress tab of your own job tracker. The tab is LABELLED "In
    Progress" and ADDRESSED as ``?stage=draft`` -- and LinkedIn renames it to
    "Draft" once you are on that url, which is why anything below about a
    "Draft" tab is what you will see if you open the link yourself. Each row
    carries title, company, location and how long ago, plus the job id and
    link, exactly as the applied list does.

    A DRAFT IS NOT AN APPLICATION. It is a distinct state that LinkedIn counts
    on a tab of its own: you opened a form, stopped, and nothing went anywhere.
    An application never has to pass through this state, so a row here is not a
    stalled application, and an empty list here is not evidence about anything
    you did send.

    AND THIS TOOL DOES NOT ANSWER WHETHER AN APPLICATION CAN BE WITHDRAWN.
    That question is open, it is recorded on linkedin_apply_job, and a draft is
    not the answer to it: discarding one of these is not the same act, because
    there is nothing on the far end to take back.

    The row's own controls were read off a capture on 2026-08-24, and this
    server performs none of them: a per-row checkbox ("Select <job title>"), a
    "Select all", an "Overflow menu", and -- never pressed from here -- a
    "Delete" control, behind a dialog this server does not act on either,
    reading "Discard draft application and remove this job?". This tool reads
    the list.

    An empty result says so explicitly and carries LinkedIn's own count for the
    tab, so "you have no drafts" and "this could not be read" are never the
    same answer.

    Args:
        limit: maximum rows to return (default 25, max 100).
    """
    limit = _clamp(limit, DEFAULT_LIMIT, MAX_LIMIT)
    try:
        return await _read_tracker(
            "draft",
            tab_label="Draft",
            limit=limit,
            surface="draft applications",
        )
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_new_messages() -> dict[str, Any]:
    """Has anything ARRIVED since you last opened Messaging? Nothing is opened.

    **THIS IS NOT AN UNREAD COUNT, and it was called one until 2026-08-26.**
    LinkedIn's nav badge counts NEW-SINCE-LAST-VISIT and **resets the moment
    you open the Messaging tab**. Measured with a genuinely unread recruiter
    InMail on screen, the badge read 0 -- because he was sitting in Messaging.
    Every conversation there was still unread. The old name,
    ``linkedin_unread_messages``, returned a true number under a false
    heading, and it is gone rather than aliased: a name that asserts something
    false should not keep working.

    So a 0 here means "nothing has landed since your last look". It does NOT
    mean your inbox is clear.

    THE UNREAD COUNT IS NOT AVAILABLE, and not for want of trying. The
    per-conversation unread markers live on the messaging list, and reaching
    that list means loading ``/messaging/`` -- which does not stay on a list.
    It redirects into ONE SPECIFIC CONVERSATION that LinkedIn chooses, so
    counting unread conversations would require opening somebody's thread,
    which is the very act that changes what is being counted.

    This never sends a message, never opens a conversation, and never loads
    the messaging surface at all. It reads the badge off your feed, which this
    server already loads. One page.

    THREE OUTCOMES, and the third is why this is not just an integer.
    ``new_since_last_visit`` is a number when the badge was read, and ``null``
    when the badge did not render -- which is NOT the same as zero and is
    never reported as zero. A badge at 0 and a nav that failed to hydrate look
    identical to any reader that collapses them, and this package has already
    lost two measurements to exactly that confusion.
    """
    try:
        async with BROWSER.session() as page:
            landed = await BROWSER.goto(page, FEED_URL)
            html = await page.content()
        verdict = shape.messaging_badge(html)
        return {
            **verdict,
            "source_url": landed,
            "opened_a_conversation": False,
            "pages_loaded": 1,
        }
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_open_messaging(
    include_names: bool = False, message_filter: str = ""
) -> dict[str, Any]:
    """Open your LinkedIn messages and report what is there. OPENS A THREAD.

    **THE COST IS IN THE NAME BECAUSE IT IS UNAVOIDABLE.** Asking LinkedIn for
    ``/messaging/`` does not stay on a list -- it redirects into ONE SPECIFIC
    CONVERSATION, and LinkedIn chooses which, not you and not this tool.
    Measured twice. So every call to this opens somebody's thread. It is
    called ``open_messaging`` rather than ``read_inbox`` because ``read_inbox``
    would describe something LinkedIn does not offer.

    WHETHER OPENING MARKS THAT MESSAGE READ IS UNMEASURED, and after three
    attempts it is believed unmeasurable from outside. The nav badge counts
    new-since-last-visit and resets when the tab is opened, so it cannot
    witness a read. The per-conversation unread markers live on this very
    page, which cannot be reached without the redirect. **The only signal that
    would settle it requires performing the act being measured.** If the
    person who wrote to you can see read receipts, they may see one. That is
    reported as an honest unknown rather than smoothed over.

    UNREAD IS PAIRED TO THE ROW. Each conversation comes back with its
    position and its own unread flag, not as a count beside a separate list of
    names. An earlier version returned "10 conversations, 4 unread markers",
    which told him four people were waiting without telling him WHICH four --
    so he still had to open LinkedIn, which is most of what this exists to
    spare him. The pairing survives redaction: "rows 1 and 4 of 10 are unread"
    is actionable without any identities at all.

    THE COUNT IS A FLOOR, NOT A TOTAL, and the result says so. This is one
    page of the list, and whether LinkedIn files InMails here or on a separate
    surface is UNMEASURED -- a recruiter InMail was seen in the product that
    did not appear in these rows. Do not report this number as everything
    waiting on you.

    NAMES ARE OFF BY DEFAULT. Pass ``include_names=True`` when you have decided
    to look. Your inbox is yours; the reason for the default is that this
    output lands in a model's context and in transcripts, where a name
    outlives the question that fetched it. The thread identifier in the landed
    url is always redacted: nothing here accepts one, so it is of no use to a
    caller and every use to a leak.

    THIS NEVER SENDS ANYTHING, and that is enforced rather than merely
    documented: LinkedIn's compose surface is on the read boundary's forbidden
    list, checked before the allowlist, so no navigation from here can reach
    it. The result also COUNTS what it found on the page it did load: editable
    nodes, form elements, and controls whose names match the vocabulary this
    server refuses. So "reading put no composer in front of you" is a number
    you can check rather than a promise you have to take.

    REACHING INMAILS TAKES A CLICK, and this tool now does it. The filter
    pills were READ rather than guessed: all six are buttons with no href, so
    that surface is not reachable by navigation, and a ``?filter=`` parameter
    would have been an invention. Pass ``message_filter="inmail"`` and the
    pill is activated.

    THAT CLICK IS SANCTIONED AND NARROW. Only seven named pills can be
    activated -- focused, other, unread, jobs, connections, inmail, starred --
    checked against a fixed list before any selector is built, so an arbitrary
    string can never become a click target. It is the second and only other
    entry in ``readonly.SANCTIONED_MUTATIONS``. A filter sends nothing and
    changes nothing on LinkedIn's servers; counted by effect it is a read, and
    it is strictly less invasive than the conversation this tool opens anyway.

    ``active_filter`` comes back in the result so a filtered page can never be
    mistaken for the whole list, and the send-surface counts are taken AFTER
    the filter is applied.

    Args:
        include_names: return correspondents' names instead of placeholders.
            Default False.
        message_filter: activate one filter pill before reading -- one of
            focused, other, unread, jobs, connections, inmail, starred. Empty
            for the default view. Anything else is refused, not clicked.
    """
    try:
        wanted = str(message_filter or "").strip().lower()
        async with BROWSER.session() as page:
            landed = await BROWSER.goto(page, MESSAGING_URL)
            applied: dict[str, Any] = {"activated": False, "why": "no filter asked for"}
            if wanted:
                # Raises for a name outside the closed set, BEFORE any click.
                applied = await dom.activate_messaging_filter(page, wanted)
                landed = page.url
            # Read AFTER the filter, so every count -- including the
            # send-surface counts -- describes the page the caller was given.
            html = await page.content()
        verdict = shape.messaging_overview(
            html, landed, include_names=bool(include_names)
        )
        # The filter pills, READ rather than assumed. This is what settles
        # whether InMails are a separate surface: if a pill is an anchor its
        # href names the filter parameter, and if it is a button with no href
        # then filtering is client-side state and InMails are unreachable by
        # navigation at all. Either answer is a finding; guessing between them
        # would make every count above untrustworthy.
        verdict["filters"] = shape.messaging_filters(html)
        verdict["active_filter"] = {
            "requested": wanted or None,
            **applied,
        }
        return {**verdict, "pages_loaded": 1}
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

    The tracker also holds Interview and Archived tabs, and they are not
    exposed as tools. Its In Progress tab is, since 2026-08-26:
    linkedin_draft_applications reads it, and this one reads Saved.

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


async def _read_save_control_state(page: Any) -> dict[str, Any]:
    """Is THIS posting saved, read off the control on the page already open.

    The exact counterpart of the follow reading beside it, and three-valued for
    the same reason: "we could not tell" has to be one of the three answers.

    IT USED TO BE THE COMMON ANSWER AND IS NOT ANY MORE. ``shape.SAVE_LABELS``
    held one row -- the OFF state -- so every saved posting came back
    ``unknown`` by construction. This function is why it no longer does: the
    three read-only observations that let the ON row be written were taken
    through it. ``unknown`` now means what it says, a control this reader
    cannot name, and is worth a human's attention rather than being the
    expected reading.

    WHY THIS IS NOT A DUPLICATE OF ``linkedin_saved_jobs``. That tool reads the
    Saved TAB, a second page, and reconciles a list against LinkedIn's own
    count; this reads the CONTROL, on a page that is already open, and costs no
    navigation. They can also disagree, and the disagreement is informative
    rather than a bug: the tab is authoritative about membership, the control
    is authoritative about what the page will do if it is clicked, and
    ``writes`` takes its direction from the first and its ANCHOR from the
    second.

    THE SECOND, WIDER LOOK RUNS ONLY ON ``unknown``, which is the rule
    ``writes._live_control`` already runs on and not a new one. A state that
    came back KNOWN was read off a label the verdict already names, so sweeping
    there would be a round trip spent on repetition. On ``unknown`` there is
    nothing to repeat -- ``read_save_control`` asks one CSS question and a page
    that answers no leaves it holding nothing at all -- so the sweep is the
    only thing that can say what was actually drawn.

    NOTHING HERE BRANCHES ON THE ANSWER and no selector is built from it.
    ``dom.save_control_selector`` still refuses every label outside
    ``dom.SAVE_LABELS_SEEN``, so a name reported here cannot become a click by
    having been reported.
    """
    control = await dom.read_save_control(page)
    verdict = dict(
        shape.save_state(control.get("label"), count=int(control.get("count") or 0))
    )
    if verdict.get("state") == shape.SAVE_UNKNOWN:
        verdict["observed"] = await dom.read_save_candidates(page)
    return verdict


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

    save_state says whether the posting is already in your saved list, read off
    the control on this same page rather than off the Saved tab, so it costs no
    extra page load. It does not change that list in either direction. Both
    states LinkedIn draws are now measured, so a posting normally comes back
    as one of them.

    'unknown' remains a real third answer and is not a synonym for no. It means
    the page drew no control this reader recognises -- most often that the page
    had not finished drawing, sometimes that LinkedIn renamed something. In
    that case you also get 'observed': the accessible names that were actually
    on the page. Those are REPORTED and nothing more -- no state is inferred
    from one, and no click can be aimed by one.

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

            reading = await dom.read_job_posting(page)
            identity = reading["identity"]
            detail = reading["detail"]

            missing = shape.job_detail_missing(detail)
            if missing:
                raise ExtractionFailedError(
                    "the job page loaded but no posting could be read from it. "
                    "Reporting the fields that did arrive would be worse than "
                    "reporting nothing: LinkedIn sets the document title on the "
                    "server, so a posting that never rendered still has a title, "
                    "and a result carrying one with no body reads as a real job "
                    "with an empty description. "
                    + shape.job_detail_failure_note(
                        missing,
                        main_present=reading["main_present"],
                        main_chars=reading["main_chars"],
                        # THE TWO PIECES OF EVIDENCE THAT SAY *WHEN*. Added
                        # 2026-08-30. BROWSER.last_settle costs nothing -- it
                        # reports a wait goto was already performing -- and it
                        # is the difference between "I looked one second after
                        # DOMContentLoaded" and "I waited the full settle and
                        # the field still was not there".
                        description_wait=reading["description_wait"],
                        settle=BROWSER.last_settle,
                    ),
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

            # AND WHETHER IT IS SAVED, off the same rendering, for the same
            # reason -- the save control sits beside the follow control on this
            # very page. Added 2026-08-30, and the reason it did not exist
            # before is worth stating because it is the reason it exists now.
            #
            # THIS IS THE ONLY READ-ONLY ROUTE TO THE SAVE CONTROL'S LABEL,
            # and it is the reason shape.SAVE_LABELS has two rows instead of
            # one. The ON label could not be observed while nothing was saved
            # on the account; the operator's first save produced it, but the
            # only instrument that could SEE it lived inside writes.perform,
            # behind a confirm token -- so re-measuring cost another supervised
            # write. A toggle whose ON label can only be read by toggling it is
            # a measurement nobody should have to pay twice for. This route
            # took the other three readings, and the row was written from all
            # four.
            #
            # IT STILL ADDS NOTHING TO THE VOCABULARY. The sweep below reports
            # names; dom.save_control_selector accepts only what is in
            # dom.SAVE_LABELS_SEEN, so a name REPORTED here cannot become a
            # click by having been reported. That property is what made it safe
            # to publish the label before anybody had decided what it meant,
            # and it is unchanged by the label since being written down.
            out["save_state"] = await _read_save_control_state(page)

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

    IT IS NOT THE ONLY SERVER-SIDE CHANGE THIS PACKAGE CAUSES, and this
    paragraph claimed it was until 2026-08-31. The old text read: "It is the
    ONE server-side change any tool here causes. Everything else in this
    package leaves LinkedIn exactly as it found it." That was true when it was
    written and is now false several times over -- FIVE writes ship and can
    change something on LinkedIn behind the gate; linkedin_open_messaging
    opens a conversation LinkedIn chooses and resets the messaging badge; and
    linkedin_search_jobs adds to his own recent-search history.

    It is corrected here rather than quietly softened, because of WHERE it
    sits: this is a docstring, an assistant answers from it, and the sentence
    it replaced is the kind a caller repeats verbatim to somebody deciding
    whether to run something. A stale reassurance is worse than no
    reassurance.

    WHAT IS STILL TRUE, and it is the narrower claim worth keeping: this is
    the only server-side change any READ in this package causes WITHOUT BEING
    ASKED FOR IT. The writes are each behind a two-call gate that performs
    nothing without a single-use token. Messaging costs what its own tool name
    says it costs. The search history is named on linkedin_search_jobs. This
    badge is the one that goes whether or not you wanted it, which is why the
    compensation below exists. linkedin_server_info's known_side_effects
    carries the full list and is the place to look rather than here.

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
# The surface census -- an instrument, not a feature
# ---------------------------------------------------------------------------

#: THE SURFACES THIS INSTRUMENT MAY READ, as a CLOSED SET of keys.
#:
#: A caller passes a KEY. A url never arrives as an argument and is never built
#: from one: an unknown key is refused with the valid keys named, and the
#: refusal RETURNS rather than falling through to a navigation. That is the
#: difference between a tool that reads a fixed set of pages and a tool that
#: reads whatever it is handed, and it is worth more than the allowlist behind
#: it -- ``BROWSER.goto`` puts every one of these through
#: ``readonly.assert_read_url`` as it does for every other read.
#:
#: THE SENTENCE THAT USED TO CLOSE THAT PARAGRAPH IS GONE, and saying so is
#: why this replaces it rather than deleting it quietly. It read: "all of them
#: were already on that allowlist before this tool existed. Nothing in
#: ``readonly.py`` was touched to add this." That was true of the first two
#: keys and stopped being true on 2026-08-30, when ``settings`` was admitted by
#: a deliberate widening, and it is now false three times over. THE COUNT WAS
#: WRONG TOO -- the paragraph said "three pages" while five keys sit below.
#: A stale count in the one comment a reader consults to learn how many
#: surfaces there are is this repo's most-repeated defect.
#:
#: NOTIFICATIONS IS DELIBERATELY ABSENT, and its absence is the one thing here
#: worth explaining, because it is the obvious third surface and the next
#: person will reach for it. Loading ``/notifications/`` CLEARS LINKEDIN'S
#: UNREAD BADGE -- measured, irreversible, and documented on
#: ``linkedin_notifications``, which is the tool that pays that cost knowingly
#: because reading the list is the whole point of it. A CENSUS of that page
#: would pay the same cost to learn what controls a notification row carries,
#: which is not worth one destroyed badge on the operator's own account. If
#: that surface ever has to be measured, do it by censusing a page that is
#: already being loaded for another reason, not by adding a key here.
#:
#: THREE MORE SURFACES WERE PUT THROUGH THAT SAME TEST ON 2026-08-30 and only
#: one of them is below. The test is not "is this page interesting" -- every
#: one of them is -- it is "does merely LOADING it cost him something". Recorded
#: here in one line each so the next person does not re-open a settled refusal;
#: the rulings and their evidence are in ``_audit/2026-08-30-linkedin-nine.md``.
#:
#: * ``/mypreferences/d/`` -- ADMITTED, below. No badge to consume, nothing a
#:   third party observes, no value changed by the load. The INDEX only: the
#:   toggles live on ``/mypreferences/d/categories/<name>`` and those are now on
#:   the forbidden substring list.
#: * ``/mynetwork/`` -- REFUSED, on the same ground as notifications. It carries
#:   the pending-invitation badge, and this package has MEASURED that family of
#:   badge resetting on load twice: notifications (documented on
#:   ``linkedin_notifications``) and messaging (documented on
#:   ``linkedin_open_messaging`` -- "counts new-since-last-visit and resets when
#:   the tab is opened"). A third member of a family whose other two members
#:   both cost a badge does not get admitted on the hope that it is the
#:   exception, and the cost of being wrong lands partly on the people whose
#:   invitations would be marked seen.
#: * MESSAGING -- REFUSED, and this one is the strongest refusal of the four
#:   because none of it is inference. ``/messaging/`` DOES NOT STAY ON A LIST:
#:   LinkedIn redirects it into one specific conversation of its own choosing,
#:   measured twice and stated on ``linkedin_open_messaging``. So a census of
#:   that key would open somebody's thread, and whether that sends them a read
#:   receipt is recorded on that tool as an honest unknown. A measurement is
#:   not worth a stranger's read receipt. It also does not need one: that tool
#:   ALREADY loads the page for a reason the operator chose, and already counts
#:   the send surface it finds there -- which is exactly the "census a page
#:   already being loaded for another reason" route named above.
#:
#: TWO MORE WERE ADMITTED ON 2026-08-31, on the operator's ruling, and each
#: gets its ruling here in the same terms the four above are judged by -- what
#: it is for, whose data it is, what LOADING it costs, and what it changes.
#:
#: * ``profile_edit_intro`` -- ``/in/me/edit/intro/``, the intro editor on HIS
#:   OWN profile. WHAT IT IS FOR: the ``update_profile_field`` capability is
#:   specced and refusing, and what it refuses on is a guessed form. This is
#:   the page that says which fields the editor really carries and how they
#:   are addressed. HIS OWN DATA, and only ever his: ``/in/me/`` redirects to
#:   whoever is signed in, and no member-slug form is on the allowlist,
#:   deliberately -- ``linkedin_who_viewed_me`` has MEASURED that loading a
#:   third party's profile leaves them a durable record, so a key that could
#:   address anybody else is refused on that ground before any other. IT
#:   CONSUMES NO BADGE and emits nothing another member can observe: an editor
#:   opened is not an activity, nothing is broadcast to a feed, and no
#:   notification reaches anyone. AND IT CHANGES NO VALUE -- the page RENDERS
#:   the fields the profile already holds. A census reads the rendered DOM and
#:   returns counts; it types nothing and submits nothing, so no draft, no
#:   revision and no artefact of any kind is left behind by loading it.
#: * ``settings_dark_mode`` -- ``/mypreferences/d/dark-mode``, ONE NAMED
#:   settings page. The ruling was explicit about the shape: one named page at
#:   a time, never the family and never a wildcard, so this is one key naming
#:   one page and a second needs a second ruling. WHAT IT IS FOR: the settings
#:   index says which sections exist; it does not say what a section page is
#:   made of, and ``update_setting`` refuses on that gap. HIS OWN DATA -- a
#:   per-account display preference with no audience and no third party
#:   anywhere in it. IT CONSUMES NO BADGE: this surface carries none, which is
#:   the same finding that admitted the index one day earlier. AND IT CHANGES
#:   NO VALUE: the page RENDERS the preference the account already holds, and
#:   a census does not touch the control that would set it.
#:   WHY THIS PAGE AND NOT ANOTHER: it is the only candidate that needed NO
#:   NARROWING OF ANY FORBIDDEN SUBSTRING. ``/mypreferences/d/settings/
#:   language`` and ``.../settings/autoplay-videos`` would each have required
#:   ``"/settings/"`` to be weakened to buy one read, and a ``categories/``
#:   page would have required weakening the entry that keeps the toggles
#:   unreachable. All three are deliberately absent. The full argument is on
#:   the pattern itself in ``readonly.py``.
CENSUS_SURFACES: dict[str, str] = {
    "feed": FEED_URL,
    "profile": f"{BASE_URL}/in/me/",
    "profile_edit_intro": f"{BASE_URL}/in/me/edit/intro/",
    "settings": f"{BASE_URL}/mypreferences/d/",
    "settings_dark_mode": f"{BASE_URL}/mypreferences/d/dark-mode",
    # THREE ADDED 2026-08-31 on the operator's rulings, each named
    # individually and never as a family.
    "post_composer": f"{BASE_URL}/preload/sharebox/",
    "article_composer": f"{BASE_URL}/article/new/",
    "messaging_compose": f"{BASE_URL}/messaging/compose/",
    # HIS OWN SUBSCRIPTION PAGE, added 2026-09-01. One question: is an InMail
    # balance a countable thing this server can read? The composer capture
    # settled that it is not on the composer.
    "premium": f"{BASE_URL}/premium/my-premium/",
}

#: WHAT A SETTLED RENDER OF EACH SURFACE LOOKS LIKE, as the control count it
#: has been MEASURED to produce. Absent means nobody has measured it enough
#: times to say, and an absent entry reports ``unknown`` rather than guessing.
#:
#: THIS EXISTS BECAUSE THE STANDING RULE WAS A RULE AND KEPT BEING FORGOTTEN.
#: The rule -- "check the control count and the landed url against what the
#: surface is known to produce before interpreting anything" -- was written
#: down on 2026-08-31 after ``profile_edit_intro`` was read TWICE at 67
#: controls and twice at 256, and the small pair was a page that had not
#: finished navigating. Two agreeing readings, both wrong.
#:
#: IT HAPPENED AGAIN THE SAME DAY, ON A DIFFERENT SURFACE, TO SOMEBODY WHO HAD
#: JUST WRITTEN THAT PARAGRAPH. ``/in/me/`` was read twice at 67 controls with
#: no redirect, where four earlier readings that day gave 232 and 233 with
#: LinkedIn's own ``isSelfProfile=true`` on the landed url. Identical
#: readings, stable, and of a page that had not arrived -- and the ONLY
#: reason it was caught is that somebody happened to remember the number 233.
#:
#: A rule a reader has to remember is a rule that works until the reader is
#: busy. So the instrument reports it: every census answer carries a
#: ``settle`` block comparing what it read against what the surface is known
#: to draw.
#:
#: IT DOES NOT REFUSE, and that is deliberate. A census is a MEASUREMENT
#: INSTRUMENT and a half-rendered page is a true reading of something -- what
#: it must never do is let that reading pass as a reading of the whole page.
#: Refusing would also make the instrument unable to measure the very failure
#: it is reporting.
#:
#: EVERY NUMBER HERE IS A MEASUREMENT, with the readings behind it named. A
#: surface measured once does not get an entry: one reading cannot establish
#: what a settled render looks like, which is the whole point.
CENSUS_SETTLED_CONTROLS: dict[str, int] = {
    # 297 (2026-08-31 am), 277, 287. The feed's count moves with what
    # LinkedIn puts in it, so the floor below does the work here rather than
    # the number.
    "feed": 277,
    # 233 (2026-08-30), 232 and 233 (2026-08-31). Then 67, twice.
    "profile": 233,
    # 255 and 256 on a settled render; 67 twice on a half-rendered one, which
    # is the pair this whole block exists because of.
    "profile_edit_intro": 255,
    # 20 controls on six readings across two days and three builds, every one
    # agreeing. The most stable surface this server reads.
    "settings_dark_mode": 20,
    # 34 (2026-08-30), 33.
    "settings": 33,
    # 31 twice, 2026-08-31, identical on every count.
    "post_composer": 31,
}

#: How far below the known count a reading may fall before it is called out.
#:
#: HALF, and the number is chosen against the two failures actually observed
#: rather than against a tolerance that felt right: both of them came in at
#: roughly a QUARTER of the settled count -- 67 of 233, and 67 of 255 -- while
#: the honest variation between settled readings of the same surface is a few
#: per cent (232 vs 233, 255 vs 256, 277 vs 287 vs 297). There is an order of
#: magnitude between the two, so anything in between is caught and nothing
#: normal is.
CENSUS_SETTLE_FLOOR = 0.5


def census_settle_report(surface: str, controls_read: int) -> dict[str, Any]:
    """How this reading compares with what the surface is known to draw.

    Three verdicts and they are three different facts:

    ``unknown``
        nobody has measured this surface enough times to say. NOT a pass --
        it is the absence of a check, and it says so.
    ``consistent``
        the reading is at or above the floor.
    ``looks_half_rendered``
        it is far below. That is a statement about THE READING, not about
        LinkedIn: the page may have been read before it arrived, which is what
        both observed instances were.
    """
    expected = CENSUS_SETTLED_CONTROLS.get(surface)
    if expected is None:
        return {
            "verdict": "unknown",
            "expected_controls": None,
            "controls_read": controls_read,
            "why": (
                "no settled control count has been measured for this surface, "
                "so this reading has nothing to be compared against. That is "
                "the ABSENCE of a check rather than a check passing -- a "
                "surface earns an entry by being read more than once and "
                "agreeing with itself."
            ),
        }
    floor = int(expected * CENSUS_SETTLE_FLOOR)
    if controls_read >= floor:
        return {
            "verdict": "consistent",
            "expected_controls": expected,
            "controls_read": controls_read,
            "why": (
                f"this surface is measured to draw about {expected} controls "
                f"when it has settled, and this reading found {controls_read}."
            ),
        }
    return {
        "verdict": "looks_half_rendered",
        "expected_controls": expected,
        "controls_read": controls_read,
        "why": (
            f"THIS READING FOUND {controls_read} CONTROLS AND THIS SURFACE IS "
            f"MEASURED TO DRAW ABOUT {expected} WHEN IT HAS SETTLED. Read it "
            "as a reading of a page that had not arrived rather than as a "
            "reading of the page. REPEATING IT DOES NOT HELP: this exact "
            "failure has been observed twice, and both times TWO readings "
            "agreed with each other and were both wrong -- repetition catches "
            "variance and cannot catch a stable wrong state. Note also that "
            "an absent control is UNKNOWN and not zero, which matters more "
            "here than anywhere: most of this page is missing."
        ),
    }


#: Surfaces whose url this server does not know until it has READ something,
#: so they cannot live in the table above.
#:
#: A SEPARATE SET RATHER THAN A PLACEHOLDER ENTRY, and the first attempt was
#: the placeholder -- ``"feed_item": BASE_URL + "/feed/update/"`` -- which
#: broke the one guard that matters most about that table:
#: ``test_every_surface_is_a_permitted_read_url`` puts every value through the
#: real read door, and a value nothing ever navigates to made that check
#: answer a question about a string nobody uses. A table where one entry is
#: not the url that gets loaded is a table a reader cannot trust the rest of.
#:
#: The resolved url still goes through the same door -- ``BROWSER.goto`` calls
#: ``assert_read_url`` like every other read -- and the shape it can take is
#: pinned by its own test against a synthetic urn.
CENSUS_RESOLVED_SURFACES: frozenset[str] = frozenset(
    {"feed_item", "feed_item_commented"}
)

#: How ``feed_item`` and ``feed_item_commented`` choose which of his items to
#: open. Both are MEASUREMENTS OF A SURFACE rather than aims for a write, and
#: the answer says which rule it used.
#:
#: ``feed_item`` takes the first in document order. That is choosing by
#: position, which this package refuses for a WRITE and which is fine here:
#: the question is what a permalink page draws, and any of his items answers
#: it equally.
#:
#: ``feed_item_commented`` takes the one with the MOST permalink anchors, and
#: it exists because the first item turned out to have no comments on it. An
#: item's anchor count is the measured signal for extra links -- his rail
#: carries six items at 2 anchors and two at 4 -- so the richest item is the
#: one most likely to render a comment count. IT IS A HEURISTIC AND SAYS SO:
#: it selects the item most likely to answer the question, and if that item
#: still draws no comment affordance the answer is that the surface does not
#: carry one, which is exactly the finding being sought.
CENSUS_ITEM_RULES: dict[str, str] = {
    "feed_item": "first",
    "feed_item_commented": "most_anchors",
}


def census_surface_keys() -> list[str]:
    """Every key this instrument answers to, resolved and direct alike."""
    return sorted(set(CENSUS_SURFACES) | CENSUS_RESOLVED_SURFACES)

#: WHAT LOADING A SURFACE COSTS, for the surfaces where the answer is not
#: "nothing". Returned ON THE ANSWER rather than only written in the
#: docstring, and that placement is the whole point: a caller reads the
#: answer, and a cost that lives only in prose is a cost the caller was not
#: told about at the moment it was paid.
#:
#: THIS TABLE EXISTS BECAUSE THIS TOOL'S OWN PROPERTY CHANGED ON 2026-08-31.
#: Every surface it measured until then RENDERED existing state and left
#: nothing behind, and its docstring said so -- notifications, /mynetwork/ and
#: messaging were refused as census keys on exactly that ground, "a census is
#: not worth a side effect". The operator has now ruled three surfaces in
#: whose load MAY leave something, knowing that. So the property is no longer
#: uniform, and the honest response is to say WHICH surfaces still have it
#: rather than to keep a sentence that is true of most of them.
#:
#: A surface absent from this table is one whose load is believed to cost
#: nothing -- believed on the same evidence as before, which is that it
#: renders state and carries no counter.
CENSUS_SURFACE_COST: dict[str, str] = {
    "post_composer": (
        "A COMPOSER MAY AUTOSAVE. This loads the post composer, types "
        "nothing and clicks nothing -- but if LinkedIn saves a draft on "
        "open, this server cannot see it: 17 candidate draft-listing "
        "addresses were run against the read boundary on 2026-08-31 and all "
        "17 were refused, so there is no reachable surface on which such a "
        "draft could be detected or removed. The operator cleared this cost "
        "knowingly. What this answer reports is what the page DREW; it does "
        "not and cannot report that nothing was left behind."
    ),
    "article_composer": (
        "A COMPOSER MAY AUTOSAVE, exactly as for post_composer above, and "
        "an article draft is the artefact most likely to persist. Same "
        "ruling, same cleared cost, same limit on what this answer can "
        "claim."
    ),
    "messaging_compose": (
        "THIS OPENS A MESSAGING SURFACE. /messaging/ is MEASURED TWICE to "
        "redirect into one conversation LinkedIn chooses, and whether the "
        "composer address does the same is UNMEASURED -- which is the "
        "question this key exists to answer. If it opens a thread it may "
        "fire a read receipt on a real person and it resets the messaging "
        "badge. The operator's ruling was conditioned on that badge reading "
        "ZERO first, so that no unread message of anybody's is spent; read "
        "it before and after through the feed or profile census, which "
        "carries it as 'Messaging, N new notifications'."
    ),
}


#: The permalink a urn is addressed by. ONE string, built from the marker the
#: activity reader already measures against, so the address this server visits
#: and the address it recognises cannot drift apart.
ITEM_PERMALINK_URL = BASE_URL + dom.ACTIVITY_PERMALINK_MARKER + "{urn}/"


async def _resolve_own_item_permalink(
    page: Any, rule: str = "first"
) -> tuple[dict[str, Any], Optional[str]]:
    """One of HIS item permalinks, or a refusal explaining why not.

    Returns ``(block, url)``. When ``url`` is ``None`` the block IS the
    answer -- a refusal to be returned whole -- and when it is a string the
    block is the ``aimed_at`` report that rides along with the census.

    THE REFUSALS ARE NOT REWRITTEN HERE. This runs the same C1 check and the
    same reader ``linkedin_my_activity_items`` runs, and forwards whatever
    they say. A second, laxer copy of an authorship rule is how the strict one
    stops being the rule -- and this caller wants a urn, which is precisely
    the caller most tempted to take one on weaker evidence.

    THE FIRST ITEM IN DOCUMENT ORDER, and the answer says so. For a WRITE that
    would be choosing by position and is refused everywhere in this package;
    for a MEASUREMENT OF THE SURFACE it is fine, because the question is what
    a permalink page draws and any of his items answers it. The distinction is
    the reason this helper lives here and not in ``writes``.
    """
    landed = await BROWSER.goto(page, SELF_PROFILE_URL)
    assert_not_authwall(landed, surface="profile")
    if not _self_assertion_on(landed):
        return (
            {
                "surface": "feed_item",
                "refused": "no_self_assertion",
                "reason": (
                    "the landed profile url carries no "
                    f"{_SELF_ASSERTION_PARAM}=true, so this server has only "
                    "its own reasoning about what /in/me/ ought to mean -- and "
                    "an item permalink is not visited on reasoning. Nothing "
                    "was read off the page and no second navigation happened."
                ),
                "authorship": _authorship_block(
                    established=False, self_assertion=False
                ),
                "pages_loaded": 1,
            },
            None,
        )
    reading = await dom.read_own_activity_items(page)
    facts = reading["authorship_facts"]
    if "items" not in reading or not reading["items"]:
        return (
            {
                "surface": "feed_item",
                "refused": reading.get("refused") or "no_items",
                "reason": (
                    reading.get("reason")
                    or "authorship held and the rail carried no item key to "
                    "aim at. An empty rail is not an error and it is not a "
                    "surface either."
                ),
                "authorship": _authorship_block(
                    established=False, self_assertion=True, facts=facts
                ),
                "counts": reading["counts"],
                "item_root_source": reading["item_root_source"],
                "pages_loaded": 1,
            },
            None,
        )
    items = list(reading["items"])
    per_item = dict(reading.get("anchors_per_item") or {})
    if rule == "most_anchors":
        # THE RICHEST ITEM, and ties break on document order so the choice is
        # deterministic across runs -- a census whose subject moved between
        # readings could not be compared with itself.
        #
        # THE ORIGINAL ORDER IS CAPTURED BEFORE THE SORT, and the first
        # version did not do that. It read ``items.index(urn)`` INSIDE the key
        # function, which ``list.sort`` evaluates while it is mutating the
        # very list being indexed -- so a urn already moved by the partial
        # sort was no longer where ``index`` looked, and the call raised
        # ``ValueError: '<urn>' is not in list``. It failed on its first live
        # use, which is the good version of that bug: loudly, before the
        # census had navigated anywhere.
        order = {urn: position for position, urn in enumerate(items)}
        items.sort(key=lambda urn: (-int(per_item.get(urn) or 0), order[urn]))
    return (
        {
            # THE URN ITSELF IS NOT REPORTED HERE. It is a real identifier and
            # it is already in the landed ``source_url`` this census returns,
            # which is one place rather than two. What this block reports is
            # HOW the aim was taken, which is the part a reader has to judge.
            "chosen_by": (
                "first item in document order on his own activity rail"
                if rule == "first"
                else "the item on his own activity rail carrying the MOST "
                "permalink anchors, ties broken by document order -- a "
                "heuristic for the item most likely to render a comment "
                "count, not a claim that it has one"
            ),
            "items_available": len(items),
            "anchors_on_the_chosen_item": int(per_item.get(items[0]) or 0),
            "authorship": _authorship_block(
                established=True, self_assertion=True, facts=facts
            ),
        },
        ITEM_PERMALINK_URL.format(urn=items[0]),
    )


@mcp.tool()
async def linkedin_surface_census(surface: str) -> dict[str, Any]:
    """Measure what controls a LinkedIn page carries. An instrument, not a feature.

    ================= WHAT THIS IS FOR -- READ FIRST =================
    THIS IS A MEASUREMENT INSTRUMENT FOR EXTENDING THIS SERVER. It is not a
    job-search tool and it will never help you find, compare or track a job.
    If you are working on the operator's job hunt, no answer you need is in
    here; use one of the other tools. It exists so that the capabilities this
    server has never measured -- publishing to a feed, replying under a
    colleague's item, reacting to one, changing a profile field, the two
    network-graph gestures, skill endorsement -- can be costed from what the
    page really carries, instead of from a guessed selector that is found to
    be wrong at the moment it would fire.
    =================================================================

    IT LOADS EXACTLY ONE PAGE, ON EVERY SURFACE BUT ONE, AND CLICKS NOTHING.
    There is no typing, no form submission, no scrolling and no request other
    than the page load. It reads the rendered DOM and returns counts. THE ONE
    EXCEPTION IS "feed_item", WHICH LOADS EXACTLY TWO: a permalink is
    addressed by a urn, and the only route to one is the same own-activity
    read linkedin_my_activity_items performs, so that surface inherits every
    authorship refusal that reader has. The count is on every answer, in
    pages_loaded, rather than only here.

    AND THE LOAD ITSELF IS NO LONGER FREE ON EVERY SURFACE. This paragraph
    used to say a census "is not worth a side effect" and used that to explain
    which pages were refused as keys. Three surfaces ruled in on 2026-08-31 --
    the two publishing composers, and the one LinkedIn opens for a new
    conversation -- may cost something merely by being opened: a composer can
    autosave a draft this server has no reachable surface to detect, and a
    /messaging/ address is measured to redirect into a real conversation. Each
    of those keys returns a "cost" field saying exactly what it may have
    spent, and the answer reports what the page DREW rather than claiming
    nothing was left behind. Surfaces with no "cost" field are the ones that
    still render state and leave nothing.

    A CONTROL BEING PRESENT IS NOT EVIDENCE THAT ACTIVATING IT IS SAFE. This
    reports that a page carries, say, a button whose accessible name is about
    reacting to a feed item. It does not establish what happens when that button
    is used, whether the result can be undone, or whether this server should
    ever be permitted to touch it. Those are separate questions and none of
    them is answered here.

    THE CENSUS REPORTS SHAPES, NEVER NAMES. The feed is made of other members,
    and LinkedIn writes their names into the accessible name of nearly every
    control on it. So each name and each href is reduced to a shape before it
    is counted -- a member path becomes /in/<member>/, an id becomes <id>, a
    possessive becomes <member>'s -- and identical shapes are merged into one
    row with a count. A COUNT OF 1 THEREFORE IDENTIFIES NOBODY: a shape seen
    once has any run of capitalised words blanked, and any control that links
    to a member is blanked whatever its count. Collecting data about other
    members is out of scope for this server and this tool is built so that it
    cannot, rather than filtered afterwards so that it does not.

    ON COMPLETENESS -- ABSENT MEANS UNKNOWN, NEVER ZERO. LinkedIn defers most
    of a feed until the page is SCROLLED and this server does not scroll, so
    what is reported is the FIRST RENDER and nothing below the fold. A control
    that does not appear here may be one screen further down, may need a menu
    opened, or may need a state this account is not in. Read a zero as "not
    seen on the first render", never as "the page has none".

    Args:
        surface: which page to measure. A KEY, never a url, and one of these
            eleven: "feed", "profile", "profile_edit_intro", "settings",
            "settings_dark_mode", "feed_item", "feed_item_commented",
            "post_composer", "article_composer", "messaging_compose" or
            "premium". THIS LIST HAS BEEN INCOMPLETE TWICE and is now pinned
            by ``test_the_census_docstring_lists_every_surface_it_answers_to``
            -- it said "five" while eight keys existed, and was then corrected
            to a NINE that named the wrong nine, listing "feed_item" while
            omitting "feed_item_commented" and "premium". The count being
            right by accident while the membership was wrong is why the test
            checks MEMBERSHIP against ``census_surface_keys()`` and not just
            the number. Several are one page
            out of a family whose other members stay unreachable, and the
            enumeration is the whole of that -- "settings" is the settings
            INDEX and nothing below it, and "settings_dark_mode" is one named
            page below it,
            while the pages carrying the actual toggles are refused by the
            read boundary. "profile_edit_intro" is the intro editor on HIS OWN
            profile, in the /in/me/ spelling that resolves to whoever is
            signed in; no other member's is reachable, because opening one
            would leave that person a durable record. "feed_item" is ONE of
            his own items, found by the own-activity reader and chosen as the
            first on the rail; no argument selects it, and a rail whose
            authorship cannot be established yields a refusal rather than a
            census. "feed_item_commented" is the same resolver under a
            different rule -- the item carrying the MOST permalink
            anchors, which is a heuristic for the richest item on his rail
            rather than a claim about what that item renders, and
            CENSUS_ITEM_RULES names the rule an answer used. "premium"
            is his own subscription page, added to settle whether an InMail
            balance is a countable thing this server can read; it is not.
            The three composer keys each carry a "cost" field saying
            what opening them may have spent. Notifications and /mynetwork/
            are still deliberately not offered: loading them consumes a badge
            he has not seen, which is a cost with nothing to show for it. See
            CENSUS_SURFACES and CENSUS_SURFACE_COST for the ruling on each.
    """
    key = str(surface or "").strip().lower()
    if key not in CENSUS_SURFACES and key not in CENSUS_RESOLVED_SURFACES:
        # A refusal that RETURNS. The unknown key must not reach a navigation,
        # so this is deliberately not an exception routed through _error --
        # there is no failure to report, only a question this tool will not be
        # asked.
        return {
            "error": "unknown_surface",
            "message": (
                f"{surface!r} is not a surface this instrument measures. It "
                "takes one of a fixed set of KEYS and never a url."
            ),
            "valid_surfaces": census_surface_keys(),
        }

    try:
        async with BROWSER.session() as page:
            pages_loaded = 1
            aimed_at: Optional[dict[str, Any]] = None
            if key in CENSUS_RESOLVED_SURFACES:
                # THE ONE SURFACE WHOSE URL THIS SERVER DOES NOT KNOW UNTIL IT
                # HAS READ SOMETHING. A permalink is addressed by a urn, and
                # the ONLY route to one here is the same reader
                # linkedin_my_activity_items uses -- which publishes a key
                # only for items it has established are his own. So this key
                # inherits that reader's whole refusal set rather than
                # weakening it: no authorship, no census.
                #
                # NO ARGUMENT SELECTS THE ITEM, and there is no parameter
                # through which one could. That is deliberate: a caller
                # handing in a urn would be handing in an identifier this
                # server never read, and the read boundary would then be the
                # only thing standing between a census and an arbitrary
                # member's item.
                aimed_at, item_url = await _resolve_own_item_permalink(
                    page, CENSUS_ITEM_RULES[key]
                )
                if item_url is None:
                    return aimed_at
                pages_loaded = 2
                final_url = await BROWSER.goto(page, item_url)
            else:
                final_url = await BROWSER.goto(page, CENSUS_SURFACES[key])
            assert_not_authwall(final_url, surface=key)
            census = await dom.read_surface_census(page)
            control_shapes, href_shapes = shape.census_aggregate(
                census["controls"]
            )
            out: dict[str, Any] = {
                "surface": key,
                "source_url": final_url,
                "counts": census["counts"],
                "control_shapes": control_shapes,
                "href_shapes": href_shapes,
                "controls_read": census["controls_read"],
                # WHETHER THIS READING LOOKS LIKE THE WHOLE PAGE. On every
                # answer rather than only on a bad one: a field that appears
                # only when something is wrong is a field a reader learns to
                # skip, and "unknown" is itself an answer worth seeing.
                "settle": census_settle_report(key, census["controls_read"]),
                "pages_loaded": pages_loaded,
                "note": (
                    "SHAPES, not names: every accessible name and href here "
                    "has had member slugs, company slugs, long ids and urns "
                    "substituted out before being counted, so a row identifies "
                    "a KIND of control and never a person. FIRST RENDER ONLY: "
                    "this loads one page and does not scroll, so a control "
                    "that is absent is UNKNOWN, not zero. And presence is not "
                    "permission -- that a control is on the page says nothing "
                    "about whether using it would be safe or reversible."
                ),
            }
            if key in CENSUS_SURFACE_COST:
                # ON THE ANSWER, not only in the docstring. See
                # CENSUS_SURFACE_COST: a cost written where the caller does
                # not look is a cost the caller was not told about.
                out["cost"] = CENSUS_SURFACE_COST[key]
            if aimed_at is not None:
                # HOW THE ITEM WAS CHOSEN, and it says "by position" out loud.
                # The rail carries several of his items and this takes the
                # FIRST in document order, which is choosing by position --
                # acceptable for a MEASUREMENT OF A SURFACE, where any of his
                # items answers the question equally, and stated rather than
                # hidden because it would not be acceptable for a write.
                out["aimed_at"] = aimed_at
            if census["truncated"]:
                out["truncated"] = True
                out["truncated_note"] = (
                    f"the page carried more than {dom.CENSUS_MAX_CONTROLS} "
                    "controls and the tail was not read. The counts block is "
                    "a whole-page count and is unaffected; control_shapes is "
                    "the distribution over what was read."
                )
            return out
    except Exception as exc:
        return _error(exc)


# ---------------------------------------------------------------------------
# The one reader that publishes names, and what buys it the right to
# ---------------------------------------------------------------------------
#
# THE TENSION, STATED BEFORE THE CODE. The census above reports SHAPES and
# never names, because a LinkedIn page is made of other members and LinkedIn
# writes their names into control labels. That gate is what makes it safe to
# point the census at a page full of strangers, and it is ALSO why
# ``linkedin_update_profile_field`` refuses: the controls it would target came
# back ``<opaque>`` from the 2026-08-31 capture of the intro editor -- read by
# the instrument and deliberately not published.
#
# THE OPERATOR RULED that a reader scoped to ONE container, MEASURED to be
# self-owned, may publish what the document-wide gate would redact. The ruling
# is narrow and its constraints are the code below rather than a note beside
# it:
#
# 1. SELF-OWNERSHIP IS ESTABLISHED PER CALL, never assumed from the fact that
#    the url said ``/in/me/``. The anchor is LinkedIn's OWN
#    ``isSelfProfile=true`` on the landed url -- an EXTERNAL assertion, which
#    is the whole reason it is the anchor rather than this server's reasoning
#    about what ``/in/me/`` ought to mean. It is measured: four landings across
#    two days, section 2d of ``_audit/2026-08-31-linkedin-finish.md``.
# 2. THE SAME MEMBER ON BOTH LANDED URLS, so the editor being read is on the
#    profile whose self-assertion was seen.
# 3. THE SEGMENT IS COMPARED AND DISCARDED. It is his member slug. It reaches
#    no return value, no log line, no exception message and no file. The tool
#    answers ``same_member: true`` and never the value, and it returns no url
#    -- only landed PATHS with the segment substituted out. The census's
#    ``source_url`` already carries his slug and that is the status quo; a
#    second place it lives is not.
# 4. THE CENSUS IS NOT TOUCHED. ``linkedin_surface_census`` and
#    ``shape.census_shape`` behave exactly as they did, so nothing already
#    published changes meaning, and no argument to the census reaches this.

#: The two pages this tool loads, spelled here as LITERALS and reachable by no
#: argument. They are the same two strings ``CENSUS_SURFACES`` holds under
#: ``profile`` and ``profile_edit_intro`` -- both already on the read
#: allowlist, and the editor already exempted for ``/edit/`` -- and
#: ``tests/test_editor_fields.py`` pins the pairs equal so the two tools can
#: never drift onto different pages while claiming the same measurement.
SELF_PROFILE_URL = f"{BASE_URL}/in/me/"
SELF_PROFILE_EDIT_INTRO_URL = f"{BASE_URL}/in/me/edit/intro/"

#: The member segment of a landed profile path. Anchored, and the trailing
#: slash is REQUIRED rather than optional: it is what makes one pattern read
#: both measured landings -- ``/in/<member>/`` on the profile, which arrives
#: with ``?isSelfProfile=true`` behind it, and ``/in/<member>/edit/intro`` on
#: the editor, which arrives with NO trailing slash of its own (section 2e of
#: the 2026-08-31 audit, where two earlier readings that said otherwise were
#: caught having sampled the page mid-flight).
_MEMBER_SEGMENT = re.compile(r"^/in/([^/?#]+)/")

#: LinkedIn's own claim that the profile just loaded is the viewer's.
_SELF_ASSERTION_PARAM = "isSelfProfile"


def _landed_path(landed_url: str) -> str:
    """The path of a landed url, with no query and no fragment."""
    return urlsplit(str(landed_url or "")).path


def _member_segment_of(landed_url: str) -> Optional[str]:
    """The ``<segment>`` of a landed ``/in/<segment>/`` path, or None.

    None means the path was not of that shape, which is a REFUSAL and not a
    fallback: every branch that reads this treats a missing segment as
    self-ownership having failed to establish.
    """
    match = _MEMBER_SEGMENT.match(_landed_path(landed_url))
    return match.group(1) if match else None


def _self_assertion_on(landed_url: str) -> bool:
    """True when LinkedIn's ``isSelfProfile=true`` rides on the landed url."""
    query = parse_qs(urlsplit(str(landed_url or "")).query)
    return any(
        str(value).strip().lower() == "true"
        for value in query.get(_SELF_ASSERTION_PARAM, [])
    )


def _path_without_member(landed_url: str, segment: Optional[str]) -> str:
    """A landed path safe to return: the member segment substituted out.

    TWO PASSES, DELIBERATELY, and the second is not decoration. The first is
    ``shape.census_substitute``, which is the same rule the census runs and
    turns ``/in/<slug>/edit/intro`` into ``/in/<member>/edit/intro``. The
    second is a LITERAL replacement of the segment this call actually captured,
    which cannot miss whatever the first pass's character class does or does
    not cover. Over-redaction is the direction to be wrong in here, and a slug
    escaping into a return value is the one failure this whole tool is built
    around.
    """
    redacted = shape.census_substitute(_landed_path(landed_url))
    if segment:
        redacted = redacted.replace(segment, "<member>")
    return redacted


def _ownership_block(
    *, established: bool, self_assertion: bool, same_member: Optional[bool]
) -> dict[str, Any]:
    """The self-ownership report, in one shape whether it held or not.

    ``how`` is present on a refusal too, and that is the point of building it
    here: a caller reading a refusal is told what WOULD have established
    ownership, so "established: false" is a statement about this call rather
    than about what the tool is able to check.
    """
    return {
        "established": established,
        "how": (
            "LinkedIn's own isSelfProfile=true assertion on /in/me/, plus the "
            "same member segment on both landed urls"
        ),
        "self_assertion_present": self_assertion,
        "same_member": same_member,
    }


@mcp.tool()
async def linkedin_profile_editor_fields() -> dict[str, Any]:
    """Name the controls inside the intro editor on HIS OWN profile.

    ================= WHAT THIS IS FOR -- READ FIRST =================
    A MEASUREMENT INSTRUMENT FOR EXTENDING THIS SERVER, as
    linkedin_surface_census is. It is not a job-search tool and no answer about
    a job is in here. It exists because linkedin_update_profile_field cannot
    name a field to type into: the census reports SHAPES and never names, so
    the controls that capability would target come back as <opaque> -- read by
    the instrument and deliberately not published.
    =================================================================

    IT LOADS TWO PAGES AND CLICKS NOTHING. Nothing is typed, nothing is
    submitted, and no request is made beyond the two page loads themselves.
    This server does not change anything about the profile here, and there is
    no argument that would let it: the tool takes none, and the two addresses
    are literals.

    IT PUBLISHES CONTROL LABELS, which the census will not do. That is a
    DELIBERATE RELAXATION of the census's privacy gate and it rests on one
    ground: self-ownership is established PER CALL -- from LinkedIn's own
    isSelfProfile=true assertion on the landed profile url, plus the same
    member segment on both landed urls -- and the container it then reads is
    the operator's own editor, holding no third party. The census itself is
    unchanged, and nothing a caller passes to it reaches this behaviour.

    IF SELF-OWNERSHIP DOES NOT HOLD, THE ANSWER CARRIES NO FIELD DATA AT ALL.
    Not an empty list beside a warning: there is no "fields" key on a refusal,
    so a refusal cannot be misread as "the container has none".

    LABELS, AND NEVER VALUES. A label is "First name"; a value is his first
    name. The second is not read: ".value" appears nowhere in the injected
    script, and no href is returned either -- only whether a control had one.

    AND THAT SENTENCE WAS FALSE UNTIL 2026-08-31, ON THE ONE CONTROL IT
    MATTERED MOST ON. LinkedIn draws the headline as a div[role=textbox] with
    no aria-label, no label-for and no title, so its accessible name resolved
    through the LAST route in the name chain -- the element's own text. For a
    contenteditable, that text IS the value, and this tool published his
    headline verbatim underneath the promise above.

    Three layers were built to keep values out and all three passed, because
    every one of them was built against the PROPERTY route: a scan of the
    script for a value read, the field dict's named keys, and a JSON sweep for
    the fixture values. A control whose NAME IS ITS CONTENT is a fourth route
    none of them covered, and no fixture in the suite had one in it.

    A control whose name is its own content now comes back as "<content>",
    with name_source "content", refused INSIDE THE PAGE so the value never
    enters this process at all. That is a different answer from "none", which
    means no name was found: this one HAS a name and it is being withheld.

    WHAT IT COSTS, said plainly: a field's current value is exactly what would
    make a CHANGE REVERTIBLE, and that is one of the two things still blocking
    linkedin_update_profile_field. Withholding it keeps the promise and leaves
    that blocker standing. Returning it would widen this tool's contract, and
    this tool exists because the operator ruled ONE narrow widening -- so a
    second one is his to rule, not a detail to settle here.

    THE CONTAINER IS FOUND STRUCTURALLY. Its anchor is not an index but the
    control whose accessible name is Save, and the container is that control's
    nearest dialog ancestor. Two such controls, or none, is a refusal rather
    than a choice, because choosing between them would be choosing by document
    order -- which is not containment.

    HIS MEMBER SLUG IS COMPARED AND DISCARDED. It is not in this answer, which
    is why the ownership block reports same_member rather than the value, and
    why the landed paths come back with the segment substituted out.

    Returns:
        pages_loaded: 2, a self_ownership block, the container descriptor and
        one record per control inside it -- or refused/reason with the same
        ownership block and no field data.
    """
    try:
        async with BROWSER.session() as page:
            landed_profile = await BROWSER.goto(page, SELF_PROFILE_URL)
            assert_not_authwall(landed_profile, surface="profile")

            # THE EXTERNAL ASSERTION FIRST. If LinkedIn does not say the
            # profile is the viewer's own, nothing further is loaded -- the
            # editor page is not fetched at all, so a call that cannot
            # establish ownership costs one page load and reads no editor.
            self_assertion = _self_assertion_on(landed_profile)
            if not self_assertion:
                return {
                    "refused": "no_self_assertion",
                    "reason": (
                        "the landed profile url carries no "
                        f"{_SELF_ASSERTION_PARAM}=true, which is LinkedIn's own "
                        "way of saying the profile is the viewer's. Without it "
                        "this tool has only its own reasoning about what "
                        "/in/me/ ought to mean, and that is not what the "
                        "relaxed gate was granted on."
                    ),
                    "self_ownership": _ownership_block(
                        established=False,
                        self_assertion=False,
                        same_member=None,
                    ),
                    "pages_loaded": 1,
                }

            profile_segment = _member_segment_of(landed_profile)
            if not profile_segment:
                return {
                    "refused": "profile_path_unreadable",
                    "reason": (
                        "the landed profile path is not of the form "
                        "/in/<member>/, so there is no member segment to "
                        "compare against the editor's."
                    ),
                    "self_ownership": _ownership_block(
                        established=False,
                        self_assertion=True,
                        same_member=None,
                    ),
                    "pages_loaded": 1,
                }

            landed_editor = await BROWSER.goto(
                page, SELF_PROFILE_EDIT_INTRO_URL
            )
            assert_not_authwall(landed_editor, surface="profile_edit_intro")
            editor_segment = _member_segment_of(landed_editor)

            paths = {
                "profile": _path_without_member(
                    landed_profile, profile_segment
                ),
                "editor": _path_without_member(landed_editor, editor_segment),
            }

            if not editor_segment:
                return {
                    "refused": "editor_path_unreadable",
                    "reason": (
                        "the landed editor path is not of the form "
                        "/in/<member>/..., so it cannot be shown to be the "
                        "same member's."
                    ),
                    "self_ownership": _ownership_block(
                        established=False,
                        self_assertion=True,
                        same_member=None,
                    ),
                    "landed_paths": paths,
                    "pages_loaded": 2,
                }
            if editor_segment != profile_segment:
                return {
                    "refused": "different_member",
                    "reason": (
                        "the two landed urls name different members, so the "
                        "editor being read is not the profile whose "
                        f"{_SELF_ASSERTION_PARAM}=true was seen. Neither "
                        "segment is reported here; that they differ is the "
                        "whole of the answer."
                    ),
                    "self_ownership": _ownership_block(
                        established=False,
                        self_assertion=True,
                        same_member=False,
                    ),
                    "landed_paths": paths,
                    "pages_loaded": 2,
                }

            ownership = _ownership_block(
                established=True, self_assertion=True, same_member=True
            )
            reading = await dom.read_self_owned_editor_fields(page)
            if "fields" not in reading:
                # The reader's own refusal, forwarded WHOLE. It knows why it
                # would not aim and this tool would only paraphrase it; the
                # ownership block is attached because ownership DID hold and a
                # caller must be able to tell that failure apart from this one.
                out = dict(reading)
                out["self_ownership"] = ownership
                out["landed_paths"] = paths
                out["pages_loaded"] = 2
                return out

            out = {
                "self_ownership": ownership,
                "landed_paths": paths,
                "container": reading["container"],
                "fields": reading["fields"],
                "pages_loaded": 2,
                "note": (
                    "LABELS, NEVER VALUES: each name here is a control's "
                    "accessible name, not what is in the control. Names are "
                    "published UNGATED -- the census's <opaque> length and "
                    "character gate is deliberately off -- because "
                    "self-ownership was established on this call and the "
                    "container holds no third party. The substitutions still "
                    "ran: a urn, a member path, a company path, a possessive "
                    "or a long digit run in a label is replaced whatever "
                    "container it was read in. FIRST RENDER ONLY: this loads "
                    "the page and does not scroll, so a control that is "
                    "absent is UNKNOWN, not zero."
                ),
            }
            if reading.get("truncated"):
                out["truncated"] = True
                out["truncated_note"] = reading["truncated_note"]
            return out
    except Exception as exc:
        return _error(exc)


def _authorship_block(
    *,
    established: bool,
    self_assertion: bool,
    facts: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """The authorship report, in one shape whether it held or not.

    THE SIBLING OF :func:`_ownership_block`, and written beside it rather than
    folded into it. The two answer different questions and their middle fields
    are not the same fields: ownership compares a member segment across TWO
    landed urls, authorship compares an author string against a heading INSIDE
    ONE page. Merging them would have produced a block with two fields that are
    null on every call, which is the shape a reader stops reading.

    ``how`` is present on a refusal too, for the reason it is there: a caller
    reading a refusal is told what WOULD have established authorship, so
    ``established: false`` is a statement about this call rather than about
    what the tool is able to check.

    ``matches_page_owner`` is a TRI-STATE and not a boolean: ``None`` means the
    comparison never happened -- there was no single author to compare, or no
    single heading to compare it against -- and ``False`` means it happened and
    the strings did not match. The brief for this slice wrote it as ``bool``;
    it is Optional here for the same reason ``checked``, ``required`` and
    ``_ownership_block``'s ``same_member`` are, and the reason is the one this
    package keeps paying for: ``False`` for "not measured" is a claim nobody
    made.
    """
    facts = dict(facts or {})
    return {
        "established": established,
        "how": (
            "LinkedIn's own isSelfProfile=true assertion on /in/me/, plus ONE "
            "author string across every overflow control on the page, plus "
            "that string and the page's h1 standing in a prefix relation. All "
            "three are required and the comparison happens inside the page. "
            "The h1's text is read through innerText first and textContent "
            "second, and owner_source says which answered -- a heading "
            "LinkedIn draws and CSS hides is still LinkedIn naming the page's "
            "owner, and the third condition is a question about the document "
            "rather than about what is on screen"
        ),
        "self_assertion_present": self_assertion,
        "authors_found": facts.get("authors_found"),
        "unanimous": facts.get("unanimous"),
        "matches_page_owner": facts.get("matches_page_owner"),
        # WHICH ROUTE READ THE HEADING, added 2026-08-31 with the second one.
        # ``None`` when no heading was found by either.
        #
        # THIS DICT IS THE THIRD ENUMERATE-AND-DROP SITE IN THIS PACKAGE and
        # it behaved exactly like the other two: the reader gained the field,
        # this block did not name it, and the tool's answer simply did not
        # carry it -- silently, with no error, in a block a caller reads to
        # decide whether an item key is trustworthy. It was caught by a test
        # asserting the field on the tool's output rather than the reader's,
        # which is the only place it could have been caught.
        "owner_source": facts.get("owner_source"),
        # WHICH HEADING ROUTE WOULD HAVE ANSWERED, separately from which route
        # DID. ``None`` here beside a non-null ``owner_source`` is the live
        # profile's exact shape -- no heading names anybody, the title does --
        # and reporting the two apart is what makes that visible rather than
        # inferable.
        #
        # THE FOURTH FIELD THIS DICT HAS DROPPED IN SILENCE, counting
        # ``container`` in the census reader, the census row's mislabelled
        # columns, ``role`` in the dark-mode projection and ``owner_source``
        # here yesterday. It is why the test below stopped asserting fields
        # one at a time and started asserting the SET.
        "owner_heading_source": facts.get("owner_heading_source"),
    }


# THE TWO MEASURED LITERALS ARE NAMED IN THE DOCSTRING BELOW, NOT QUOTED, AND
# THAT IS NOT STYLE. ``readonly.docstring_write_claims`` scans every tool
# description for an unnegated write verb, and both strings carry one:
# ``Open control menu for post by `` contains ``post`` and ``/feed/update/``
# contains ``update``. Quoting either turns this READ into a tool whose
# description claims a write, and ``test_no_docstring_claims_a_write`` fails --
# MEASURED, not predicted: the first draft of this docstring quoted both and
# the check reported exactly those two contexts, plus a third from the words
# ``commit message``. The literals live in ``dom.ACTIVITY_OVERFLOW_PREFIX`` and
# ``dom.ACTIVITY_PERMALINK_MARKER`` beside the census readings that measured
# them, which is one grep away and is where a measured string belongs anyway.
# Pasting them back here is a build failure, not a review comment.
@mcp.tool()
async def linkedin_my_activity_items() -> dict[str, Any]:
    """Item keys for the posts on HIS OWN profile that HE wrote.

    ================= WHAT THIS IS FOR -- READ FIRST =================
    THE AIMING READER. linkedin_comment_on_item and linkedin_react_to_item are
    registered, specced and refusing, and the blocker was never the read
    boundary or the click anchor -- both are in hand. They are UNAIMABLE: no
    other tool here returns an item key. linkedin_surface_census substitutes
    every urn out before it counts, by design, so a measurement cannot publish
    an identifier; and the feed carries zero item permalinks. This tool returns
    the keys, for his own items only.
    =================================================================

    DO NOT PASTE ITS OUTPUT INTO A TRACKED FILE IN THIS REPOSITORY. The urns
    here are REAL identifiers for real posts, this repository is public, and
    tests/test_no_committed_identity.py sweeps every tracked file for exactly
    this shape -- urn:li:<type>:<six or more digits> -- and will fail the
    build. Quoting one in a commit, a fixture, an audit note or a docstring
    is the failure that guard exists to catch.

    IT LOADS ONE PAGE AND CLICKS NOTHING. /in/me/, and no argument selects a
    surface, because there is no other surface this could be pointed at: the
    same census that measured this rail measured /feed/ carrying ZERO item
    permalinks and EIGHT DIFFERENT authors, which is a page this tool would
    refuse on both counts.

    AUTHORSHIP IS ESTABLISHED, NOT INFERRED FROM PLACEMENT, and it takes all
    three of these on every call:

    1. LinkedIn's own isSelfProfile=true on the landed url of /in/me/.
    2. UNANIMITY -- every control on the page whose accessible name starts
       with the measured overflow prefix carries the SAME author, and there
       is at least one. An activity rail carries reshares and other people's
       items, so this is the condition that does the work: if every overflow
       control names one person, no pairing can attribute an item to somebody
       else. The prefix is the literal string LinkedIn writes and this server
       does not choose; it is dom.ACTIVITY_OVERFLOW_PREFIX, quoted there
       beside the census reading that measured it.
    3. That one author is the PAGE OWNER, compared against the page's own h1.
       Either string may be a prefix of the other, because LinkedIn is measured
       to write a shortened form of his name into the overflow label while the
       h1 carries the full one.

    IF AUTHORSHIP CANNOT BE ESTABLISHED THE ANSWER CARRIES NO ITEM KEYS AT ALL.
    There is no "items" key on a refusal -- not an empty list -- so a refusal
    can never be read as "he has no items". The counts are still reported,
    because every one of them is an integer.

    NO NAME EVER LEAVES THE PAGE. The author string and the h1 text are read,
    compared and discarded inside the document; only booleans and counts come
    back. That is why the report says matches_page_owner rather than naming
    either string, and it is the same discipline the invitation reader keeps.

    A URN IS PUBLISHED ONLY IF IT IS ANCHORED-SHAPE AND PAIRED. The segment
    between the permalink marker in an href and the next delimiter must match
    urn:li:<letters>:<digits> exactly, or it is counted unrecognised and
    dropped; and it must sit inside an item root that itself contains an
    overflow control, or it is counted unpaired and dropped. The marker is
    dom.ACTIVITY_PERMALINK_MARKER, quoted there beside its measurement.
    item_root_source reports which route found each root -- LinkedIn's own
    [data-urn] or [data-id] marker, or this server climbing ancestors until it
    found one.

    Returns:
        An authorship block, counts, item_root_source and pages_loaded 1 --
        plus items and anchors_per_item only when authorship was established.
    """
    try:
        async with BROWSER.session() as page:
            landed = await BROWSER.goto(page, SELF_PROFILE_URL)
            assert_not_authwall(landed, surface="profile")

            # C1 FIRST, AND THE PAGE IS NOT READ IF IT FAILS. The same order
            # linkedin_profile_editor_fields uses and the same helper: if
            # LinkedIn does not say the profile is the viewer's own, no script
            # is injected at all, so a call that cannot establish C1 reads no
            # author string and no heading. The refusal it returns therefore
            # carries no counts either, and that absence is the honest one --
            # nothing was counted.
            self_assertion = _self_assertion_on(landed)
            if not self_assertion:
                return {
                    "refused": "no_self_assertion",
                    "reason": (
                        "the landed profile url carries no "
                        f"{_SELF_ASSERTION_PARAM}=true, which is LinkedIn's own "
                        "way of saying the profile is the viewer's. Without it "
                        "this tool has only its own reasoning about what "
                        "/in/me/ ought to mean, and an item key is not "
                        "published on reasoning."
                    ),
                    "authorship": _authorship_block(
                        established=False, self_assertion=False
                    ),
                    "pages_loaded": 1,
                }

            reading = await dom.read_own_activity_items(page)
            facts = reading["authorship_facts"]

            if "items" not in reading:
                # The reader's own refusal, forwarded WHOLE. It knows which of
                # C2 and C3 failed and this tool would only paraphrase it. The
                # authorship block is rebuilt here because C1 DID hold and a
                # caller must be able to tell that failure apart from this one.
                return {
                    "refused": reading["refused"],
                    "reason": reading["reason"],
                    "authorship": _authorship_block(
                        established=False,
                        self_assertion=True,
                        facts=facts,
                    ),
                    "counts": reading["counts"],
                    "item_root_source": reading["item_root_source"],
                    "pages_loaded": 1,
                }

            out: dict[str, Any] = {
                "authorship": _authorship_block(
                    established=True, self_assertion=True, facts=facts
                ),
                "items": reading["items"],
                "anchors_per_item": reading["anchors_per_item"],
                "counts": reading["counts"],
                "item_root_source": reading["item_root_source"],
                "pages_loaded": 1,
                "note": (
                    "REAL IDENTIFIERS: every string in items addresses a real "
                    "post and must never be pasted into a tracked file in this "
                    "repository -- tests/test_no_committed_identity.py sweeps "
                    "for exactly this shape and this repository is public. "
                    "HIS ITEMS ONLY: a urn is here because every overflow "
                    "control on the page named one author, that author and the "
                    "page's h1 stand in a prefix relation, and the urn was "
                    "paired to an item root carrying such a control. FIRST "
                    "RENDER ONLY: this loads the page and does not scroll, so "
                    "an item that is absent is UNKNOWN, not one he did not "
                    "write. counts.unrecognised and counts.unpaired are urns "
                    "this reader saw and would not publish, which is the "
                    "difference between what is on the page and what is in "
                    "this list."
                ),
            }
            if reading.get("truncated"):
                out["truncated"] = True
                out["truncated_note"] = reading["truncated_note"]
            return out
    except Exception as exc:
        return _error(exc)


# ---------------------------------------------------------------------------
# The five writes
# ---------------------------------------------------------------------------
#
# THIS BANNER SAID "The two writes" over FIVE of them until 2026-08-31, and the
# body under it said "they are the only two in the package" -- the same
# carried-count rot the module docstring records, in the one place a reader
# scrolling for the write boundary is most likely to stop. The count is
# ``len(writes.PERFORMABLE)`` and it is pinned in
# ``tests/test_server_surface.py``.
#
# EVERYTHING ABOVE THIS LINE READS. These five do not, and they are the only
# five in the package: save_job, unsave_job, apply_job, unfollow_company and
# follow_company. Each is two-step by construction: called without a
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
    # follow_company WAS HERE UNTIL 2026-08-30. Its line was accurate and it
    # is now in the wrong place: the slug-to-id gap it described is real, was
    # re-measured that day, and belongs on the SPEC in reversible_by, which
    # the confirm block prints. Deciding for him on a ground he can read for
    # himself is what moved.
    "set_open_to_work": (
        # NARROWED 2026-08-30, and the old sentence is quoted because it is the
        # exact failure mode this dict keeps producing. It read: "its editor is
        # not addressed by a url at all -- 237 urls and 37 payload paths
        # measured across five profile captures, zero of which reach it."
        #
        # THE EVIDENCE WAS TRUE OF THE CAPTURES AND IS FALSE OF THE SITE. A
        # live census of his profile on 2026-08-30 found THREE editors carried
        # as ordinary anchors -- /in/<member>/edit/intro/,
        # /in/<member>/edit/forms/summary/new/ and
        # /in/<member>/overlay/contact-info/ -- plus 2 forms where the fixtures
        # carry none. So "a profile editor is not url-addressed" is refuted.
        #
        # WHAT SURVIVES, and it is narrower and still decisive: NONE of those
        # three anchors, and no other href on the page, reaches the OPEN TO
        # WORK audience editor. That one remains modal-only.
        "no url reaches its editor. NARROWED 2026-08-30 after a live census "
        "refuted the wider claim this entry used to make: profile editors ARE "
        "url-addressed -- three of them are plain anchors on his own profile, "
        "and the live page carries 2 forms where every frozen fixture here "
        "carries none. What survives is specific to this setting: none of "
        "those anchors, and no other href on the page, reaches the Open To "
        "Work audience editor. It opens as a modal, and the click that would "
        "first show it is also the first that could change it. This is the "
        "one setting here a current employer can see."
    ),
    # THE SEVEN, added 2026-08-30. Kept to one line each on purpose: the full
    # argument for every one of them lives in ``writes._NINE_REFUSALS``, which
    # is what a caller actually hits when it refuses, and two long copies of
    # one argument drift apart. What each line has to carry is the SHAPE of
    # the blocker, because "no control has been observed" and "the address is
    # forbidden" want completely different work to lift them.
    "publish_post": (
        "the surface and the anchor are MEASURED as of 2026-08-31 and this "
        "line said the opposite until 2026-09-01: /preload/sharebox/ is on "
        "the read allowlist, loads with no redirect, draws contenteditable "
        "== 2 and names its publish control 'Post'. What stops it is TYPING, "
        "for which no mutation is sanctioned, AND the absence of a reliable "
        "verification -- the only surface that could confirm a post exists "
        "is his own activity rail, and that rail is measured to render "
        "intermittently."
    ),
    "comment_on_item": (
        "BOTH of the blockers this line named until 2026-09-01 are closed. "
        "The item permalink is on the read allowlist, and the comment box "
        "was observed on it: contenteditable == 1, a div with role=textbox "
        "named 'Text editor for creating comment'. What stops it is TYPING "
        "AND THE ABSENCE OF A COUNT -- 91 controls on that permalink and not "
        "one of them totals comments, on a page where the reactions total "
        "reads out fine."
    ),
    # ``"react_to_item"`` LEFT THIS TABLE ON 2026-09-01 BECAUSE THE ACTION
    # SHIPS. Three of its four blockers closed on 2026-08-31; the fourth --
    # which reaction the toggle applies -- did not close and was RULED ON
    # instead. It is now a disclosure printed from the spec's ``residue``,
    # which is where a fact he must read before confirming belongs, rather
    # than here where it decided for him.
    "update_profile_field": (
        "'/edit/' is on the forbidden-url list, so the three editor "
        "addresses measured live on 2026-08-30 are refused before the "
        "allowlist is consulted. One exact-url exemption was ruled in on "
        "2026-08-31, for the intro editor in its own-profile spelling, and "
        "that one surface is now a census key; no field inside any editor "
        "has been observed."
    ),
    "update_setting": (
        "the STATE is now measured -- dark mode is a three-state radio group "
        "and exactly one reports checked, read off the page that carries the "
        "value rather than the index that lists addresses -- so this no "
        "longer refuses for want of a direction. It refuses because the "
        "action has NO WRITE SURFACE: mint declines a grant at issue, so no "
        "confirm_token can exist for it. The rest of the family stays "
        "forbidden by '/mypreferences/d/categories/' and '/settings/'; note "
        "before ruling on it that 'Close and delete account' and 'Hibernate "
        "account' are in it."
    ),
    # ``"send_invitation"`` LEFT THIS TABLE ON 2026-09-01. Its aim closed --
    # aim_invitation resolves his own needle to exactly one control, with the
    # comparison run inside the page -- and its verification did not, so the
    # gate now DECLARES that nothing can confirm a sent invitation rather than
    # refusing over it.
    "send_message": (
        "'/messaging/compose' is on the forbidden-url list, and one "
        "exact-url exemption was ruled in on 2026-08-31, so the composer HAS "
        "now been observed -- this line said it never had until 2026-09-01. "
        "What stops it is TYPING AND the absence of anything that could "
        "verify a send: no countable total on the composer, and none on "
        "/premium/my-premium/ either. The preview still costs nothing -- it "
        "reads the nav badge and stops; linkedin_open_messaging is the tool "
        "that opens a thread knowingly."
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


async def _write_tool(
    action: str,
    target: Any,
    confirm_token: str,
    to_state: Optional[str] = None,
) -> dict[str, Any]:
    """Preview or perform, for EVERY write tool on this surface.

    ONE implementation, because the writes differ only in their spec and a
    second copy is a second place for the gates to drift apart. ``target`` is
    whatever the spec's ``target_kind`` says it is -- a job id for the save
    pair, a numeric company id for the unfollow -- and it is normalised by
    ``writes._target_for`` rather than here, so a tool cannot accept a shape
    its own action does not address.

    ``to_state`` NAMES THE DESTINATION for an action that is not a binary
    toggle, and it was ADDED 2026-08-31 to fix a gap rather than to extend a
    feature. ``writes._direction`` has carried a multi-state branch since
    August -- the one ``dacf76d`` hardened that morning against a ``KeyError``
    on its origin -- and **nothing could reach it**: this function was the only
    caller of ``preview`` and it passed no destination, so every multi-state
    action refused with "the destination must be named rather than derived"
    whatever it was asked. A guard on an unreachable branch is a guard nobody
    can be sure of, and that branch is now reachable and exercised.

    It stays ``None`` for the five binary toggles, and ``_direction`` ignores
    it for them -- a destination handed to a two-state action would be a
    caller choosing an outcome the state already determines.
    """
    if not writes.writes_enabled():
        return _writes_off(action)
    spec = writes.spec_for_action(action)
    async with BROWSER.session() as page:
        if not str(confirm_token or "").strip():
            return await writes.preview(
                spec,
                target=target,
                navigator=BROWSER,
                page=page,
                to_state=to_state,
            )
        grant = writes.consume(
            str(confirm_token).strip(),
            action=action,
            # THE RAW TARGET, NOT A STRING OF IT. It used to be
            # ``str(target ... ).strip()``, which for a composite action is
            # the repr of a mapping and can never equal what ``mint``
            # canonicalised -- so a composite action's token was unredeemable
            # by construction. ``consume`` now normalises through the same
            # ``writes._target_for`` ``mint`` uses, which is the only way the
            # two doors can agree, and it needs the value rather than a
            # rendering of it.
            target=target,
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
    """Remove one job posting from your saved list. Two calls, and a real one.

    Same two-step shape as ``linkedin_save_job`` and the same gates: no
    confirm_token, no action -- you get a block to read and a token that works
    once, within two minutes.

    THIS DOCSTRING SAID THE OPPOSITE UNTIL 2026-08-30, and the reversal is
    worth stating rather than quietly editing away. It read "THIS TOOL CANNOT
    PERFORM ANYTHING TODAY", because LinkedIn names the save control by what
    it will DO, and the name it wears on a saved posting had never been
    observed -- there was nothing saved on this account to observe it on. That
    was true, and it was circular: the only way to see the label was to save
    something. A save was performed, the label was measured four times across
    two independent routes, and it is now in the table. The anchor is real.

    IT STILL REFUSES, and the refusal is now NARROW rather than total: it acts
    only from a state it recognises. A posting whose control it cannot read,
    or reads under a name nobody has measured, is refused rather than clicked.
    On a toggle that is the difference that matters, because acting from the
    wrong state performs the opposite action -- an unsave fired on an unsaved
    posting saves it.

    A SECOND BLOCKER IS LIVE AS OF 2026-08-30 AND IT IS NOT THIS TOOL'S FAULT.
    The preview takes its DIRECTION from your Saved tab, and that list cannot
    currently be read: the rows draw, and the harvest returns none of them.
    Until that is fixed the preview refuses with "the current state of this
    target came back 'unknown'" and mints no token. So this tool is capable and
    not yet reachable end to end. ``linkedin_saved_jobs`` fails the same way
    and prints what it saw.

    WHAT AN UNSAVE COSTS YOU, since the gate will ask. It drops a posting you
    chose to keep, and this server has no record of what your list held before
    -- so "undo" means finding the posting again and saving it, which is only
    easy while you still know which one it was.

    Args:
        job_id: the numeric LinkedIn job id, as it appears in /jobs/view/<id>.
        confirm_token: leave empty to preview. A token from that preview, used
            once within two minutes, performs the unsave.
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
async def linkedin_follow_company(
    job_id: str, confirm_token: str = ""
) -> dict[str, Any]:
    """Follow the company that posted one job, from the posting page itself.

    Same two-step shape and the same five gates as ``linkedin_save_job``.
    PERFORMED FROM 2026-08-30, and this tool did not exist before that date --
    the action was specced in August and deliberately not offered.

    READ THE ASYMMETRY BEFORE YOU USE IT, because it is the whole reason this
    was held back. A follow IS reversible -- LinkedIn writes the inverse into
    the control's own accessible name, ``Following``, and into two other
    surfaces besides -- but THIS SERVER CANNOT AIM THE UNDO. A posting names
    its employer by SLUG; ``linkedin_unfollow_company`` addresses rows by
    NUMERIC COMPANY ID; and nothing resolves one to the other. That was
    re-measured on 2026-08-30 by the cheapest available route:
    ``linkedin_job_detail`` on a live posting returns
    ``company_url: .../company/<slug>/``, a slug and not an id. Manage Pages
    also renders about twenty rows of however many you follow with no
    pagination, so a newly followed Page may not even appear there.

    So: reversible in LinkedIn, and by hand. Not by this server. The preview
    says exactly that in ``reversible_by`` and it is why you are reading it
    here as well.

    THE DIRECTION IS READ OFF THE POSTING, at no extra page load -- the state
    and the action share a page, which is the best shape a gate can have. The
    control is measured: ``aria-label="Follow"`` when not following and
    ``"Following"`` when following. A posting that has not hydrated draws
    neither, and the preview refuses on ``unknown`` rather than clicking.

    Verification after the click is the WEAKEST in this server: the control
    redraws in place and is re-read there, because a follow's preview reads
    the posting rather than a list that could be counted before and after.
    ``performed`` may come back ``"unknown"``; open your followed companies
    and look rather than retrying, since a retry on a toggle that did land
    performs the opposite.

    Args:
        job_id: the numeric LinkedIn job id whose employer you want to follow.
        confirm_token: leave empty to preview. Pass the token from that
            preview to actually follow.
    """
    try:
        return await _write_tool("follow_company", job_id, confirm_token)
    except Exception as exc:
        return _error(exc)


# ---------------------------------------------------------------------------
# The seven that are built, gated, and refuse
# ---------------------------------------------------------------------------
#
# ADDED 2026-08-30 on the standing ruling that whatever is technically possible
# should be achieved. Each is a full spec behind the SAME two-call gate as the
# writes above -- one target normaliser, one live read, one reversibility
# verdict, one refusal in its own words -- and NONE of them can act.
#
# WHY THEY ARE REGISTERED AT ALL RATHER THAN LEFT OUT. The server's own
# instructions said until this morning: "There is no message, no connection
# request, no InMail, no profile edit, and no post -- do not look for them or
# suggest they exist." That sentence was true and it was also the worst
# possible answer to give somebody who wants to know whether LinkedIn can be
# posted to from here, because it conflates "this server will not" with "you
# cannot". A tool that appears, reads the surface live, and says precisely
# which measurement is missing is discoverable and honest; a silence is
# neither. It is the same argument that keeps the write tools registered when
# LINKEDIN_ENABLE_WRITES is unset.
#
# NONE OF THEM WIDENED THE READ BOUNDARY. Each previews by loading a page that
# was already allowed -- the feed, his own profile, the settings index -- and
# the four frozen denylists are byte-identical across the change that added
# them.


@mcp.tool()
async def linkedin_publish_post(text: str, confirm_token: str = "") -> dict[str, Any]:
    """Publish a post to your feed. BUILT, GATED, AND REFUSING.

    Call it and it reads the feed live, then tells you what it found and why it
    will not act. It cannot publish anything today and the reason is not that
    the code is missing.

    WHAT IS MEASURED: the feed carries one composer control, accessible name
    ``Start a post``, drawn as a div with role=button and no href -- so the
    composer is a MODAL, not a page. Two publish routes ARE addressed by url
    and both are real anchors: ``Write article`` at /article/new/ and
    ``Create a post`` at /preload/sharebox/.

    WHAT IS NOT: the same census counted ZERO contenteditable nodes on the
    page, so the editor itself, and whatever control publishes, have never
    been observed. This server does not click a control it has not seen. And
    neither publish address is on its read allowlist.

    WHAT IT WOULD COST IF IT COULD. A post is a BROADCAST under your own name
    -- your profile reports 275 followers and LinkedIn's own analytics show
    past posts reaching 103, 308 and 1,284 impressions. Whether a post can be
    deleted at all is UNMEASURED here: the per-post overflow menu renders
    collapsed and its items have never been read, and deletion is permanently
    forbidden in this server in any case. It is also the one artefact here a
    current employer sees without looking for it.

    WHAT WOULD LIFT THE REFUSAL: a capture of the opened composer -- the
    accessible name of its editable node and of its publish control. The click
    that first SHOWS the composer publishes nothing; only the second one does.

    Args:
        text: the exact words that would be posted. They are part of the
            target, so a confirm token is bound to them and cannot be redeemed
            against different words.
        confirm_token: accepted, and no token is ever issued for this action.
    """
    try:
        return await _write_tool("publish_post", {"text": text}, confirm_token)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_comment_on_item(
    item: str, text: str, confirm_token: str = ""
) -> dict[str, Any]:
    """Comment under one feed item. BUILT, GATED, AND REFUSING.

    Reads the feed live, then refuses and says what it saw.

    WHAT IS MEASURED: the comment affordance, in both of its two shapes, and
    they are not the same control. On the feed it is a text-named button that
    opens a composer in place. On a profile it is an ANCHOR pointing at the
    item's permalink, /feed/update/<urn>/ -- which is the only place a target
    key for a feed item has ever been seen.

    WHAT IS NOT, and there are three: the permalink family is on this server's
    forbidden-url list, so the item cannot be opened; the comment box is a
    contenteditable node and the census counted zero of them, so it has never
    been observed; and the exact form of a feed urn is unmeasured, because the
    census substitutes ``<urn>`` out before counting so that it cannot publish
    an identifier.

    WHAT IT WOULD COST. A comment is PUBLIC, ATTRIBUTED TO YOU, and sits under
    SOMEBODY ELSE'S item -- published to their audience rather than to your
    followers, and it notifies them. Whether it can be deleted is unmeasured
    here and this server could not delete it either way.

    Args:
        item: which feed item, by whatever identifier you have. This server has
            never read one unshaped, so it does not pretend to validate the
            form -- and it also cannot act on it.
        text: the exact words. Part of the target, so a token binds to them.
        confirm_token: accepted, and no token is ever issued for this action.
    """
    try:
        return await _write_tool(
            "comment_on_item", {"item": item, "text": text}, confirm_token
        )
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_react_to_item(
    item: str, confirm_token: str = ""
) -> dict[str, Any]:
    """React to one feed item, under your own name. PERFORMS, behind the gate.

    THIS DOCSTRING SAID "BUILT, GATED, AND REFUSING" UNTIL 2026-09-01, which
    would now be the most load-bearing false sentence on this surface -- a
    caller reads this INSTEAD of the source. It refused on four grounds. Three
    were measured away and the fourth was ruled on, and the difference between
    those two ways of stopping refusing is the thing to carry out of here.

    WHAT CLOSED BY MEASUREMENT, all on 2026-08-31:

      * THE ADDRESS. The item permalink ``/feed/update/<urn>/`` was on the
        forbidden-url list and is now on the read allowlist, addressed by the
        urn shape the activity reader emits and nothing wider.
      * THE AIM. The permalink draws EXACTLY ONE reaction control where the
        feed and your profile draw eight, so choosing one is no longer
        choosing by position.
      * THE TARGET. ``linkedin_my_activity_items`` returns keys for items
        measured to be yours.

    WHAT DID NOT CLOSE, AND SHIPS ANYWAY BECAUSE HE RULED IT SO: **pressing
    this control applies whatever LinkedIn's default reaction is, and nobody
    has measured which one that is.** ``Open reactions menu`` is a separate
    control beside the toggle and has never been opened. If pressing turns out
    to open a picker rather than apply immediately, this gate REPORTS THAT and
    chooses nothing from it. The confirm block prints all of this before you
    confirm; it is in the spec's ``residue`` rather than here, so it reaches
    the person deciding rather than only the person reading source.

    THE ANCHOR is the strongest in this package: LinkedIn writes the toggle
    state into the control's own accessible name,
    ``aria-label="Reaction button state: no reaction"``, read on the feed, on
    your profile, and on the permalink itself. The control states its own
    state, so the direction is not inferred from anything around it.

    THE VERIFICATION IS REAL AND IT IS NARROW. After the click the permalink
    is re-rendered and the control re-read: present and no longer wearing the
    off label means it moved. It CANNOT say what it moved to, because the
    ON-state label has still never been observed. That is a different question
    from whether it moved, and it is named rather than blurred -- a check that
    answers "whether" honestly is not the same as one that could not pass,
    which is what ``apply_job`` carried until 2026-08-31.

    WHAT IT COSTS. A reaction NOTIFIES THE AUTHOR and can surface in your own
    network's feed. Taking it back later -- if that is possible, which is
    still unmeasured -- removes the row and not the notification, and not
    whatever was shown to whoever saw it.

    Args:
        item: which feed item, as ``urn:li:activity:<digits>``. Get it from
            ``linkedin_my_activity_items``, which returns keys only for items
            established to be yours.
        confirm_token: leave empty to read the gate. NEVER confirm on his
            behalf: a token from that block, used once within two minutes, is
            the only thing that acts.
    """
    try:
        return await _write_tool("react_to_item", item, confirm_token)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_update_profile_field(
    field: str, value: str, confirm_token: str = ""
) -> dict[str, Any]:
    """Change one field on your own profile. BUILT, GATED, AND REFUSING.

    Reads your profile live, then refuses and says what it found.

    WHAT IS MEASURED, and it CONTRADICTS what this server used to say. Profile
    editors ARE addressed by url. Three are ordinary anchors on your own
    profile -- ``/in/<member>/edit/intro/``,
    ``/in/<member>/edit/forms/summary/new/`` and
    ``/in/<member>/overlay/contact-info/`` -- and the live page carries 2
    forms where every frozen fixture in this repo carries none. This server
    reported for a week that the profile editor "is not addressed by a url at
    all"; that was true of the captures and false of the site.

    WHAT IS NOT: ``/edit/`` is on the forbidden-url list, so those addresses
    are refused before the allowlist is even consulted, and no field inside
    any editor has ever been observed -- so even given the address there is
    nothing measured to type into.

    WHAT IT WOULD COST. Your profile is what recruiters read, continuously
    rather than at a moment you choose -- it reports 29 profile views. An edit
    reverted an hour later was still live for an hour, and LinkedIn notifies a
    network about some profile changes, which this server has not measured and
    would not control.

    Args:
        field: which field. Named freely; nothing here validates it against a
            list of fields, because no editor has been opened to enumerate one.
        value: the new value. Part of the target, so a token binds to it.
        confirm_token: accepted, and no token is ever issued for this action.
    """
    try:
        return await _write_tool(
            "update_profile_field", {"field": field, "value": value}, confirm_token
        )
    except Exception as exc:
        return _error(exc)


#: The settings whose VALUE this server can read, keyed by their normalised
#: name. ONE, and a second needs a second ruling -- the operator's words were
#: one named page at a time, never the family, never a wildcard.
#:
#: WHY THIS TABLE EXISTS AT THE TOOL rather than inside the reader.
#: ``writes.observe`` chooses its surface from the SPEC's own ``state_from``
#: and never from an argument, which is the property that stops a caller
#: pointing this server at a page of its choosing. The consequence is that the
#: reader opens the dark-mode page whatever ``setting`` was asked for, so
#: without a guard HERE a question about "language" would be answered with
#: dark mode's state wearing the label of the setting asked about.
READABLE_SETTINGS: dict[str, str] = {"dark mode": writes.DARK_MODE_URL}


def _normalise_setting(name: str) -> str:
    """Lower-case, and every run of non-alphanumerics becomes one space.

    So ``Dark Mode``, ``dark-mode`` and ``dark_mode`` all reach the same key,
    while nothing that is not that setting is quietly admitted. Deliberately
    NOT a fuzzy match: a gate that guesses which setting was meant is a gate
    that can act on the wrong one.
    """
    return re.sub(r"[^a-z0-9]+", " ", str(name or "").lower()).strip()


@mcp.tool()
async def linkedin_update_setting(
    setting: str, value: str, confirm_token: str = ""
) -> dict[str, Any]:
    """Change one account setting. Two calls, and the first is free.

    THIS DOCSTRING SAID "BUILT, GATED, AND REFUSING" UNTIL 2026-08-31 and the
    reversal is stated rather than quietly edited away, because a caller who
    read the old text would decline to offer this and would be wrong.

    CALL IT WITHOUT ``confirm_token`` FIRST. Nothing is done: the setting's
    own page is read live and you get back a block naming which of its three
    states the account is in, which way the change would move it, where that
    was read from, and how it can be undone. Read it, then call again with the
    ``confirm_token`` it hands you. The token works ONCE, only for this
    setting AND this destination, and it expires in two minutes -- so a
    scheduled or unattended caller can never hold a live one.

    WHAT IS MEASURED. Dark mode is a THREE-STATE RADIO GROUP -- ``Always
    off``, ``Always on``, ``Device settings`` -- named through
    aria-labelledby, and EXACTLY ONE of them reports checked. Six readings
    across two days and three builds agree on every count: 20 controls, ZERO
    forms, 16 links, no dialogs, and no redirect. The control that gets
    clicked is the one named for the DESTINATION, and the selector is built
    from the role that control actually carries rather than an assumed one.

    THE VERIFICATION IS A FRESH NAVIGATION AND A RE-READ OF THE GROUP. Not the
    control reporting on itself: the page is loaded again and the browser's
    own checked property is read across all three, so a control that redrew
    wrongly would have to report itself checked AND the other two report
    themselves unchecked to pass. ``performed`` comes back ``true``, ``false``
    or ``"unknown"``; on ``"unknown"`` do not retry -- open the page and look.

    WHAT IT COSTS YOU, and it is the least of any write here: dark mode is a
    per-account DISPLAY preference. It has no audience, no other member can
    observe it, it is broadcast nowhere, and the same tool sets it back. That
    is why it is the one settings page that was admitted.

    ONE SETTING IS WRITABLE, AND ASKING ABOUT ANY OTHER LOADS NOTHING. The
    read allowlist admits exactly one page below the settings index, admitted
    BY NAME on the operator's ruling. ``/mypreferences/d/categories/`` and
    ``/settings/`` are both on the forbidden-url list.

    READ THIS BEFORE ASKING FOR THE FAMILY TO BE OPENED. ``Close and delete
    account`` and ``Hibernate account`` are addresses in it. A permission
    written for the FAMILY would carry those with it, which is why a setting
    is admitted by name or not at all -- and it is why this tool shipping does
    NOT mean the next setting is a small step.

    Args:
        setting: which setting, by name. Matched case- and
            punctuation-insensitively against the one writable setting; any
            other name returns a refusal and opens no page at all.
        value: the destination, named rather than derived, because this
            setting has three states and no direction can be inferred from
            two. Part of the target, so the token binds to it: confirming with
            a different value than the preview showed is refused.
        confirm_token: leave empty to preview. Pass the token from that
            preview to actually change the setting.
    """
    if _normalise_setting(setting) not in READABLE_SETTINGS:
        # A REFUSAL THAT RETURNS, AND THAT LOADS NOTHING, mirroring
        # linkedin_surface_census's unknown-key branch. It has to live here
        # rather than in the reader: writes.observe picks its surface from the
        # SPEC's own state_from and never from an argument, so the reader
        # opens the dark-mode page whatever setting was asked for. Without
        # this, a call about "language" would come back describing dark mode's
        # state as though it were the answer -- a gate confidently reporting a
        # measurement of the wrong thing, which is worse than one that refuses.
        return {
            "error": "unreadable_setting",
            "message": (
                f"{setting!r} is not a setting this server can read a value "
                "for, so it cannot say which way a change would move it -- "
                "and it will not act on one it cannot describe. "
                "Nothing was loaded. Exactly one settings page below the "
                "index is on the read allowlist, admitted BY NAME on the "
                "operator's ruling that a setting is admitted by name or not "
                "at all -- the family also contains 'Close and delete "
                "account' and 'Hibernate account'."
            ),
            "readable_settings": sorted(READABLE_SETTINGS),
            "pages_loaded": 0,
        }
    try:
        return await _write_tool(
            "update_setting",
            {"setting": setting, "value": value},
            confirm_token,
            to_state=value,
        )
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_send_invitation(
    member: str, confirm_token: str = ""
) -> dict[str, Any]:
    """Send one connection invitation. PERFORMS, behind the gate, and CANNOT BE CONFIRMED.

    THIS SAID "BUILT, GATED, AND REFUSING" UNTIL 2026-09-01. Two things
    changed and they are different in kind, which is the part to carry out of
    here.

    THE AIM CLOSED, by measurement. It refused because the accessible name of
    an invitation control IS the other person's name -- a string this server
    will not read -- so the only measurable part, the suffix " to connect",
    selected all nine controls on the page. You now supply a NEEDLE: your own
    word for the person. The comparison runs INSIDE THE PAGE, so the name
    never reaches this process, and exactly one match is the only aimable
    answer. **Two matches refuse rather than shortlist**, because an
    invitation that reaches whoever was drawn first is precisely the failure
    worth refusing.

    THE VERIFICATION DID NOT CLOSE, AND THIS SHIPS ANYWAY BECAUSE HE RULED IT
    SO. **Nothing this server can read will tell you whether the invitation
    was sent.** The confirm block says so in three parts -- what would confirm
    it, why this server cannot reach that, and what you must do yourself --
    and the result block repeats them, because the sentence you need after
    acting is the last one. In short: open My Network, then Manage, then Sent,
    and look.

    Two separate measured reasons put that surface out of reach, and either
    would be enough on its own: its address contains "invitation", which is on
    the forbidden-url list and is checked before the allowlist; and reaching
    it goes through /mynetwork/, whose load CONSUMES your pending-invitation
    badge. No post-click state has ever been observed on the page this DOES
    act on, either, so it cannot even report that the control changed.

    WHERE IT ACTS, and why that page: your OWN profile draws nine invitation
    controls and costs NO badge. No third party's profile is ever loaded --
    that would leave them a durable record, which is the one thing this whole
    family of rulings refuses to spend.

    IT CANNOT BE TAKEN BACK by this server, and whether LinkedIn offers a
    withdraw at all is UNMEASURED -- which is a stronger statement than this
    server lacking one. The surface that would show it is the same one that is
    out of reach.

    Args:
        member: YOUR OWN WORD for the person -- a name fragment that picks
            out exactly one of the invitation controls on your profile. It is
            handed into the page and compared there; it is never used to
            discover anybody, and this server reads no names back out of the
            match except the single label it shows you in the preview to
            confirm your word selected who you meant.
        confirm_token: leave empty to read the gate. NEVER confirm on his
            behalf -- this one reaches another person.
    """
    try:
        return await _write_tool("send_invitation", member, confirm_token)
    except Exception as exc:
        return _error(exc)


@mcp.tool()
async def linkedin_send_message(
    member: str, text: str, confirm_token: str = ""
) -> dict[str, Any]:
    """Send a message or InMail. BUILT, GATED, AND REFUSING.

    THIS PREVIEW DOES NOT OPEN MESSAGING, and that is deliberate rather than
    incidental. Loading /messaging/ is MEASURED TWICE to redirect into one
    specific conversation of LinkedIn's own choosing -- so the load itself
    OPENS SOMEBODY'S THREAD, and whether that fires them a read receipt is an
    honest unknown believed unmeasurable from outside. The nav badge also
    counts new-since-last-visit and resets when the tab is opened. A gate that
    opened messaging in order to describe that cost would have spent it, on a
    third party, to produce a sentence.

    So it reads the BADGE off a page already open -- that number is the
    counter a load would consume -- and stops. If you want the surface
    measured, call ``linkedin_open_messaging`` yourself: it pays that cost
    knowingly and its own name says so.

    WHAT IS NOT MEASURED: any composer. ``/messaging/compose`` is on this
    server's forbidden-url list -- it is the entry that SURVIVED when the
    blanket messaging ban was narrowed in August so you could read your own
    inbox, and it was kept for exactly this.

    WHAT IT WOULD COST. A message is read by a person, usually within a day,
    and arrives as an email as well as a notification; it is the most
    irreversible-in-audience action in this whole design, and unlike an
    application it is addressed to a named individual rather than a company's
    process. It MAY ALSO SPEND AN INMAIL CREDIT, which is unmeasured rather
    than denied: messaging outside your network uses InMail, that allowance is
    finite on Premium Career, and this server has never read your balance
    because the page carrying it is not on the read allowlist.

    Args:
        member: who to message. Unvalidated, for the same reason as
            ``linkedin_send_invitation``.
        text: the exact words. Part of the target, so a token binds to them.
        confirm_token: accepted, and no token is ever issued for this action.
    """
    try:
        return await _write_tool(
            "send_message", {"member": member, "text": text}, confirm_token
        )
    except Exception as exc:
        return _error(exc)



#: Fields that answer "what is running and what can it do". Everything else in
#: server_info is REASONING -- why a thing is refused, what would measure it,
#: who ruled and when -- which is worth having and is not worth paying for on
#: every routine call.
#:
#: MEASURED BEFORE IT WAS SPLIT, because the whole point is a number: the full
#: block was ~3136 tokens, and one field (not_yet_measured, the twelve-item
#: roadmap with each entry naming its instrument) was 772 of them -- 24.6% of
#: a call that a client makes to find out what version is running.
#:
#: WHAT DELIBERATELY STAYS IN THE DEFAULT, because a short answer that drops
#: a hazard is not an improvement:
#:   * irreversible -- names what cannot be undone. 149 tokens, and the one
#:     thing a caller must not have to ask twice for.
#:   * known_side_effects -- reading the notifications page clears a badge.
#:   * recovery_path and rate_discipline -- both small and both operational.
#:   * writes_available / writes_sanctioned -- the capability answer itself.
_INFO_CORE: frozenset[str] = frozenset(
    {
        "name",
        "version",
        "build",
        "read_only",
        "capabilities",
        "writes_available",
        "writes_sanctioned",
        "irreversible",
        "known_side_effects",
        "recovery_path",
        "rate_discipline",
        "browser",
    }
)


def _trim_info(full: dict[str, Any], verbose: bool) -> dict[str, Any]:
    """The lean view, plus a pointer saying exactly what was left out.

    THE POINTER IS NOT DECORATION. A caller handed a short dict with no note
    cannot tell a lean default from a server that has stopped reporting its
    boundary -- and this package spent a day on the difference between an
    absence and a decision. omitted lists the field NAMES, so the answer to
    "is the reasoning still there" is visible without a second call.
    """
    if verbose:
        return full
    lean = {k: v for k, v in full.items() if k in _INFO_CORE}
    omitted = sorted(k for k in full if k not in _INFO_CORE)
    lean["omitted"] = {
        "fields": omitted,
        "why": (
            "These carry the server's REASONING -- what it refuses and why, "
            "what has never been measured and what would settle it, who ruled "
            "on what and when. All of it is still here; none of it is needed "
            "to find out what is running. Call "
            "linkedin_server_info(verbose=True) for the full block."
        ),
        "nothing_about_safety_was_omitted": (
            "irreversible, known_side_effects and recovery_path are in the "
            "default above. Reversibility text also stays inline on every "
            "tool that writes -- linkedin_apply_job's own docstring carries "
            "the finding that nobody has established LinkedIn offers a "
            "withdraw at all, and that reaches a caller at confirm time "
            "rather than behind this flag."
        ),
    }
    return lean


@mcp.tool()
async def linkedin_server_info(verbose: bool = False) -> dict[str, Any]:
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
        full = {
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
                "unsave_job became performable on 2026-08-30 and this field "
                "said it REFUSED to act until that day: the accessible name "
                "LinkedIn gives the save control on a saved posting had never "
                "been observed on this account. The operator's first save "
                "produced it, three read-only re-measurements agreed, and it "
                "is in the table. It still refuses from any state it does not "
                "recognise, and its preview is separately blocked while the "
                "Saved tab cannot be read -- direction comes from that list. "
                "unfollow_company is "
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
                # EMPTY, AND THAT IS THE POINT OF THE FIELD. Everything that
                # was ever listed here has been built:
                #
                #   applying              -> linkedin_apply_job    2026-08-25
                #   the unread count      -> linkedin_new_messages 2026-08-25
                #   reading the inbox     -> linkedin_open_messaging
                #
                # The field stays, and stays empty, because an entry here is a
                # standing embarrassment by design -- something measured to
                # WORK that is not being done -- and the answer to one is to
                # build it rather than to justify it. Keeping the field means
                # the next such thing has somewhere to be visible instead of
                # being quietly reasoned away.
            ],

            # CONVENTIONS THAT DID NOT SURVIVE A QUESTION. Kept as a record
            # because all three were refusals this server presented as though
            # they were limits, and in each case the operator asked why and
            # there was no answer that held.
            "conventions_lifted": [
                "READING HIS OWN INBOX, 2026-08-25. Filed as POLICY on the "
                "reasoning that opening a conversation costs a third party "
                "something. It does not: those people wrote to HIM. The test "
                "for that list is whether the cost lands on somebody who is "
                "not him, and this failed it.",
                "APPLYING, ENDORSING, LOOKING UP ONE MEMBER, 2026-08-25. Filed "
                "as POLICY alongside genuine third-party protections. Bulk "
                "collection deserved refusing; a single named lookup is what "
                "the product is for, and an endorsement is a gift rather than "
                "an extraction. The limit that mattered moved INTO the code as "
                "a per-call cap.",
                "REACHING INMAILS, 2026-08-26. This server's own verdict said "
                "they were unreachable 'without interacting with the page, "
                "which it does not do' -- a design decision written as if it "
                "were a platform limit, and read as one. It can click; a "
                "filter pill sends nothing and changes nothing on LinkedIn, so "
                "by effect it is a read; and this server already opens a "
                "conversation and may fire a read receipt. Refusing the lesser "
                "act while performing the greater one is backwards.",
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
                "CHANGING account settings. Still unmeasured, but the "
                "obstacle named here until 2026-08-30 was NOT REAL and the "
                "correction is worth carrying: this entry used to say "
                "/settings/ is on the forbidden substring list. It is -- and "
                "that substring was measured on 2026-08-30 to match NOTHING "
                "LinkedIn serves. The surface is /mypreferences/d/, and the "
                "legacy address /psettings/ does not contain '/settings/' "
                "either, because the character before 'settings/' is a 'p'. "
                "Both were refused, but by the allowlist alone, with no "
                "second gate behind it. WHAT CHANGED: the settings INDEX is "
                "now a census surface (linkedin_surface_census "
                "surface='settings') on a written side-effect ruling, the "
                "category pages that carry the toggles are now genuinely on "
                "the forbidden substring list, and nobody has run the census "
                "yet. So what is missing is the MEASUREMENT and no longer the "
                "means of taking it: run that census and enumerate the "
                "sections, recording for each whether it is url-addressed or "
                "a modal.",
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

            # THE POLICY BUCKET WAS DISSOLVED BY THE OPERATOR ON 2026-08-25.
            # Recorded here rather than quietly dropped, because a refusal
            # list that shrinks without a name on it is indistinguishable
            # from drift.
            #
            # He read the three entries back -- reading his own inbox,
            # endorsing a member's skill, and looking up one member -- and
            # ruled: "if they're technically possible via the MCP, why should
            # we not do that? Let's do them also."
            #
            # WHAT THE BUCKET GOT WRONG, which is worth being exact about
            # because "the operator overruled a safety line" would be the
            # wrong lesson. Its test was sound: an entry belongs here only if
            # the cost lands on somebody who is not him. Its MEMBERSHIP was
            # not. Reading his own inbox is his own correspondence -- those
            # people wrote to HIM. An endorsement is a gift to the person
            # receiving it, not an extraction from them. And looking up ONE
            # named member is what the product is for; the thing that ever
            # deserved refusing was BULK COLLECTION, which is a different act
            # rather than a bigger version of the same one.
            #
            # SO THE PROTECTION DID NOT DISAPPEAR, IT MOVED INTO THE CODE.
            # The limit that mattered is now a hard cap inside the lookup
            # tool -- one member per call, no enumeration, no walking a
            # connection graph, no iterating search results into profile
            # fetches, and nothing about another member persisted past the
            # response. A line in a bucket relies on a caller's restraint; a
            # line in the tool does not.
            "policy_dissolved": (
                "TWO OF THE THREE entries were dissolved by the operator on "
                "2026-08-25: reading his own inbox, and looking up a member. "
                "This field records who did it and when, so a future reader "
                "can tell a deliberate dissolution from a list that quietly "
                "lost entries. "
                "ONE REMAINS, AND IT WAS NOT PART OF THAT RULING: driving an "
                "off-site applicant-tracking system. He was asked about three "
                "LinkedIn capabilities and ruled on those; the ATS refusal is "
                "a different kind of thing -- not a LinkedIn capability at "
                "all, but somebody else's form on somebody else's domain -- "
                "and a ruling is not extended past what it covered, least of "
                "all to remove a protection. "
                "THE LIMIT THAT SURVIVED THE LOOKUP is no longer a refusal, "
                "it is a cap inside the tool: ONE member per call, no "
                "enumeration, no persistence. Bulk collection is what "
                "LinkedIn's detection actually hunts, the account it would "
                "cost is the one his referrals run through, and this "
                "repository is public under his real name -- a harvester here "
                "is a durable public artifact in a way a lookup is not."
            ),
            "refused_as_policy": [
                # TWO ENTRIES LEFT THIS LIST ON 2026-08-25, dissolved by the
                # operator -- reading his own inbox, and looking up a member.
                # See policy_dissolved above for who ruled and why the bucket
                # was wrong in its MEMBERSHIP rather than in its test.
                #
                # THIS ONE WAS NOT PART OF THAT RULING and is not the same
                # kind of thing. He was asked about three LinkedIn
                # capabilities; driving a third party's applicant-tracking
                # system is not a LinkedIn capability at all. It is somebody
                # else's form on somebody else's domain, under their terms,
                # and a ruling is not extended past what it covered -- least
                # of all to remove a protection nobody was asked about.
                "DRIVING AN OFF-SITE APPLICANT-TRACKING SYSTEM. Protects: the "
                "third party whose form and domain it is. linkedin_job_detail "
                "already reports apply_path and names the destination host, so "
                "a caller learns where the application would go; reporting and "
                "stopping is the behaviour, and it is not a gap.",
            ],
            # SIDE EFFECTS THIS SERVER PAYS, and the two it REFUSES to pay.
            # The refused pair is listed here rather than only in a document
            # because a caller meets this field and does not meet the audit:
            # the whole design of linkedin_send_message and
            # linkedin_send_invitation is that they DO NOT incur these, and a
            # cost that is never named cannot be weighed.
            "known_side_effects": [
                "opening the notifications page clears the unread badge",
                "running a job search adds to your own recent-search history",
                "opening messaging clears the messaging badge AND opens one "
                "conversation LinkedIn chooses -- measured twice. Only "
                "linkedin_open_messaging and linkedin_new_messages can incur "
                "this, and only when called. linkedin_send_message "
                "deliberately does NOT open messaging: it reads the nav badge "
                "off a page already loaded and refuses.",
                "loading /mynetwork/ would consume the pending-invitation "
                "badge, which is why no tool here loads it at all. "
                "linkedin_send_invitation reads the invitation controls on "
                "your own profile instead, a surface carrying no such counter.",
                "loading another member's profile leaves them a durable "
                "record -- linkedin_who_viewed_me reads the receiving end of "
                "exactly that signal, 365 days back. No tool here loads a "
                "third party's profile, which is also why endorsing a skill "
                "cannot be measured from this server.",
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
        return _trim_info(full, verbose)
    except Exception as exc:
        return _error(exc)


def main() -> None:  # pragma: no cover - process entry point
    logging.basicConfig(level=logging.WARNING)
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
