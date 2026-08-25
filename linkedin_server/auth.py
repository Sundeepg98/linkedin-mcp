"""Is there a live session? Answered by asking LinkedIn, never by a cookie.

This is the module that a sibling server got wrong yesterday: it reported
success the moment a session cookie appeared, and an anonymous cookie issued
to a signed-out visitor looks exactly like a signed-in one. So the rule here
is absolute and it is the whole design:

    **A cookie is only ever a reason to ASK. It is never an answer.**

The question is put to ``/voyager/api/me``, which is the call LinkedIn's own
web app makes on page load to find out who you are. Signed in, it returns your
identity. Signed out, it refuses. Three outcomes are reported, not two:

* ``authenticated: true``  -- the endpoint answered with an identity.
* ``authenticated: false`` -- the endpoint refused (401/403), or the feed
  bounced us to an auth wall.
* ``authenticated: null``  -- neither could be established. "I could not
  tell" must not collapse into "you are signed out", or this server will
  cheerfully tell the operator to sign in again while his session is fine.

On the headers: the request carries ``csrf-token`` (LinkedIn's own web app
copies it from the ``JSESSIONID`` cookie) and the Rest.li protocol headers,
because the endpoint will not answer without them. Those are protocol, not
disguise -- the user agent, TLS stack and IP are the browser's real ones, and
nothing here spoofs a fingerprint or imitates human timing.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Optional

from linkedin_server.config import (
    AUTHWALL_MARKERS,
    API_TIMEOUT_MS,
    FEED_URL,
    LOGIN_POLL_S,
    LOGIN_RECHECK_S,
    LOGIN_URL,
    LOGIN_WAIT_S,
    ME_API,
    logger,
)
from linkedin_server.errors import (
    AuthUnknownError,
    BrowserUnavailableError,
    NotAuthenticatedError,
)

#: The cookie that carries a LinkedIn session. Its presence is a prompt to
#: ask the API, and that is the only role it has anywhere in this server.
#: It is a PERSISTENT cookie, which is what makes the profile a durable login.
SESSION_COOKIE = "li_at"

#: LinkedIn's web app sends this cookie's value back as the csrf-token header,
#: and the identity endpoint will not answer an authenticated request without
#: it. Unlike ``li_at`` this one is a SESSION cookie -- measured in this very
#: profile's cookie store as ``is_persistent=0, expires=NULL`` -- so it is
#: GONE every time the browser restarts, while the login itself is not.
#:
#: That asymmetry is a trap: on a cold start the jar holds a perfectly good
#: ``li_at`` and no ``JSESSIONID``, the identity call goes out with no csrf
#: token, and a server that stopped there would tell the operator to sign in
#: again while his session was fine. :func:`_warm_session_cookies` is the fix
#: -- one load of a LinkedIn page makes LinkedIn issue a fresh one.
CSRF_COOKIE = "JSESSIONID"

#: Upper bound on how many times one login wait may spend a request.
LOGIN_MAX_CHECKS = 40

AUTH_ENDPOINT_NOTE = f"GET {ME_API}"

#: This server's name inside the shared auth-lifecycle shape, carried as a
#: FIELD rather than left to be inferred from a tool prefix. Four servers in
#: this family return this shape, and a reader holding two results at once
#: should not have to parse a tool name to tell them apart.
SERVER_ID = "linkedin"

#: Which route produced an expiry date. Both routes read the SAME jar, by two
#: different means, and the difference is not cosmetic: a date read off disk
#: means the browser could not be started, so it arrives next to a null
#: verdict, while a date read out of a live context arrives next to a real
#: one. Naming the route keeps a reader from having to work that out.
LIVE_EXPIRY_SOURCE = "the live browser context's cookie jar, read through Playwright"
DISK_EXPIRY_SOURCE = (
    "the profile's on-disk cookie jar (Default/Network/Cookies), read from a "
    "copy with no browser launched"
)


# ---------------------------------------------------------------------------
# The measurement
# ---------------------------------------------------------------------------


async def _cookie_records(page: Any) -> list[dict[str, Any]]:
    """Read the raw cookie jar. Never logged, never persisted, never returned.

    Values stay inside this module. Only derived facts -- a name, a presence,
    an expiry timestamp -- ever reach a tool result.
    """
    try:
        jar = await page.context.cookies("https://www.linkedin.com")
    except Exception as exc:
        raise BrowserUnavailableError(
            f"could not read the browser session: {type(exc).__name__}: {exc}"
        ) from exc
    return [c for c in (jar or []) if isinstance(c, dict)]


async def _cookies(page: Any) -> dict[str, str]:
    """Read the browser's cookie jar as name -> value."""
    return {c.get("name", ""): c.get("value", "") for c in await _cookie_records(page)}


async def _warm_session_cookies(page: Any, cookies: dict[str, str]) -> tuple[
    dict[str, str], Optional[str]
]:
    """Make LinkedIn issue the session cookies a cold browser does not have.

    Returns the (possibly refreshed) cookie map and the FINAL url of the load,
    or ``None`` if no load was needed or it failed.

    Only fires when :data:`CSRF_COOKIE` is missing, which in practice means
    "this browser has just started". One page load, through the ordinary
    allowlist and rate gate. A failure here is not fatal: the caller carries
    on with the cookies it already had and the identity endpoint gets the last
    word, exactly as it would have without this step.
    """
    if CSRF_COOKIE in cookies:
        return cookies, None

    from linkedin_server.browser import BROWSER

    try:
        final_url = await BROWSER.goto(page, FEED_URL)
    except Exception as exc:
        logger.info(
            "cold-start warm-up navigation failed: %s: %s", type(exc).__name__, exc
        )
        return cookies, None

    try:
        refreshed = await _cookies(page)
    except BrowserUnavailableError:
        return cookies, final_url

    logger.debug(
        "cold-start warm-up: %s %s after loading the feed",
        CSRF_COOKIE,
        "issued" if CSRF_COOKIE in refreshed else "still missing",
    )
    return refreshed, final_url


def _csrf_from(cookies: dict[str, str]) -> Optional[str]:
    raw = cookies.get(CSRF_COOKIE)
    if not raw:
        return None
    return raw.strip('"')


def _identity_from(payload: Any) -> dict[str, Any]:
    """Pull a name and public identifier out of a /me response, defensively.

    Voyager has moved this payload around more than once, so every field is
    optional and a miss returns ``{}`` rather than a guess.
    """
    if not isinstance(payload, dict):
        return {}
    candidates: list[dict[str, Any]] = []
    data = payload.get("data")
    if isinstance(data, dict):
        candidates.append(data)
        mini = data.get("miniProfile")
        if isinstance(mini, dict):
            candidates.append(mini)
    included = payload.get("included")
    if isinstance(included, list):
        candidates.extend(e for e in included if isinstance(e, dict))

    for entry in candidates:
        first = entry.get("firstName")
        last = entry.get("lastName")
        public_id = entry.get("publicIdentifier")
        if first or public_id:
            out: dict[str, Any] = {}
            name = " ".join(p for p in (first, last) if p).strip()
            if name:
                out["member"] = name
            if public_id:
                out["public_identifier"] = public_id
                out["profile"] = f"https://www.linkedin.com/in/{public_id}"
            if out:
                return out
    return {}


async def check_auth(
    page: Any, *, corroborate: bool = False, warm: bool = True
) -> dict[str, Any]:
    """Ask LinkedIn whether this session is signed in.

    Args:
        page: a live Playwright page from the persistent-profile context.
        corroborate: when the API answer is inconclusive, also load the feed
            and look at where it lands. Costs one page load, so tools that
            are mid-flow (the login wait) leave it off.
        warm: on a cold browser, load one LinkedIn page first so LinkedIn
            issues the session cookie its identity endpoint requires. Must be
            OFF while the operator is typing into the sign-in form -- the
            warm-up navigates, and navigating would throw his half-filled
            login page away.

    Returns:
        A dict with ``authenticated`` (``True`` / ``False`` / ``None``),
        ``checked_against``, and a ``reason`` whenever the answer is not
        ``True``. Never raises for a plain signed-out session -- that is an
        answer, not an error.
    """
    cookies = await _cookies(page)
    warm_final_url: Optional[str] = None
    if warm:
        cookies, warm_final_url = await _warm_session_cookies(page, cookies)
    cookie_present = SESSION_COOKIE in cookies

    headers = {
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "x-restli-protocol-version": "2.0.0",
    }
    csrf = _csrf_from(cookies)
    if csrf:
        headers["csrf-token"] = csrf

    status: Optional[int] = None
    body_text = ""
    try:
        response = await page.request.get(
            ME_API, headers=headers, timeout=API_TIMEOUT_MS
        )
        status = response.status
        try:
            body_text = await response.text()
        except Exception:
            body_text = ""
    except Exception as exc:
        logger.info("auth check request failed: %s: %s", type(exc).__name__, exc)
        result = {
            "authenticated": None,
            "checked_against": AUTH_ENDPOINT_NOTE,
            "session_cookie_present": cookie_present,
            "reason": (
                f"the auth request could not be completed ({type(exc).__name__}: "
                f"{exc}). This is not a verdict either way."
            ),
        }
        return await _maybe_corroborate(page, result, corroborate, warm_final_url)

    base = {
        "checked_against": AUTH_ENDPOINT_NOTE,
        "http_status": status,
        "session_cookie_present": cookie_present,
    }

    if status == 200:
        try:
            payload = json.loads(body_text) if body_text else {}
        except ValueError:
            payload = {}
        identity = _identity_from(payload)
        if identity or payload:
            return {"authenticated": True, **base, **identity}
        return await _maybe_corroborate(
            page,
            {
                "authenticated": None,
                **base,
                "reason": (
                    "the endpoint returned 200 but an empty body, which is "
                    "neither a signed-in identity nor a refusal."
                ),
            },
            corroborate,
            warm_final_url,
        )

    if status in (401, 403):
        return {
            "authenticated": False,
            **base,
            "reason": (
                "LinkedIn refused the identity call, so there is no live "
                "session. Call linkedin_login and sign in yourself in "
                "the window it opens."
                + (
                    " A li_at cookie is present but it is not a valid session; "
                    "cookie presence is never proof of a login."
                    if cookie_present
                    else ""
                )
            ),
        }

    return await _maybe_corroborate(
        page,
        {
            "authenticated": None,
            **base,
            "reason": (
                f"the identity call returned HTTP {status}, which is neither an "
                "identity nor a refusal. LinkedIn returns 999 to requests it "
                "declines to serve; treat this as unknown, not as signed out."
            ),
        },
        corroborate,
        warm_final_url,
    )


async def _maybe_corroborate(
    page: Any,
    result: dict[str, Any],
    corroborate: bool,
    known_final_url: Optional[str] = None,
) -> dict[str, Any]:
    """Second, independent read: does the feed bounce us to an auth wall?

    Only ever used to turn an UNKNOWN into a ``false``. It is never allowed to
    manufacture a ``true`` -- landing on the feed proves rather less than the
    identity endpoint answering, and this server does not upgrade a verdict on
    weaker evidence.

    ``known_final_url`` is where the cold-start warm-up already landed. When
    it is set the corroboration is free: the feed has been loaded once this
    call and loading it twice would spend a second request to re-read an
    answer already in hand.
    """
    if not corroborate:
        return result

    if known_final_url:
        final_url = known_final_url
    else:
        from linkedin_server.browser import BROWSER

        try:
            final_url = await BROWSER.goto(page, FEED_URL)
        except Exception as exc:
            logger.info(
                "corroborating navigation failed: %s: %s", type(exc).__name__, exc
            )
            return result

    result = dict(result)
    result["corroborated_with"] = f"GET {FEED_URL} -> {final_url}"
    if any(marker in final_url for marker in AUTHWALL_MARKERS):
        result["authenticated"] = False
        result["reason"] = (
            "the identity call was inconclusive, but loading the feed landed on "
            f"{final_url}, which is LinkedIn's signed-out wall. Call "
            "linkedin_login and sign in yourself."
        )
    return result


# ---------------------------------------------------------------------------
# How long the session lasts, reported rather than assumed
# ---------------------------------------------------------------------------


def _cookie_expiry(record: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Turn one raw cookie record into the facts worth reporting.

    Playwright reports ``expires`` as seconds since the epoch, or ``-1`` for a
    cookie that dies with the browser. Only derived facts leave here: the
    value itself never appears in a result.
    """
    if record is None:
        return {"present": False}

    raw = record.get("expires")
    try:
        expires = float(raw)
    except (TypeError, ValueError):
        expires = -1.0

    if expires <= 0:
        return {
            "present": True,
            "persistent": False,
            "expires_at": None,
            "note": (
                "a session cookie: it lives only as long as the browser "
                "process does, and a fresh one is issued on the next page load."
            ),
        }

    remaining = expires - time.time()
    return {
        "present": True,
        "persistent": True,
        "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expires)),
        "expires_in_days": round(remaining / 86400.0, 1),
        "expired": remaining <= 0,
    }


def _credential(
    facts: dict[str, Any],
    *,
    expiry_source: str,
    unreadable: Optional[str] = None,
) -> dict[str, Any]:
    """Render ``li_at`` as the shared shape's ``credential`` block.

    ``facts`` is a :func:`_cookie_expiry` record. ``unreadable`` carries the
    reason the jar could not be read AT ALL, when that is what happened -- an
    absent cookie and an unreadable jar are different facts and they do not
    share a field. The first says "you are signed out"; the second says "I
    could not look", and an operator acts differently on each.

    Only derived facts appear here. The cookie's value is not among them and
    is not available to this function: :func:`_cookie_expiry` never carried
    one out of the record it was handed.
    """
    present = bool(facts.get("present"))
    persistent = bool(facts.get("persistent"))
    dated = present and persistent and facts.get("expires_at") is not None

    if dated:
        source = expiry_source
    elif unreadable:
        source = f"no date could be read: {unreadable}"
    elif not present:
        source = (
            f"there is no {SESSION_COOKIE} in the jar, so there is no date to "
            "read. That is what a profile nobody has signed in to looks like."
        )
    else:
        source = (
            f"{SESSION_COOKIE} is in the jar but carries no expiry, which "
            "makes it a session cookie that dies with the browser rather than "
            "the year-long persistent one a signed-in profile holds."
        )

    return {
        "kind": "cookie",
        "name": SESSION_COOKIE,
        "present": present,
        "format": "cookie" if present else "absent",
        "expires_at": facts.get("expires_at") if dated else None,
        "expires_in_days": facts.get("expires_in_days") if dated else None,
        # Never False as a stand-in for "unknown". No readable date means the
        # question cannot be answered from here, and that is a null.
        "expired": facts.get("expired") if dated else None,
        "expiry_source": source,
        # LinkedIn honours the date it stamped on the cookie, so as an answer
        # to "when does this lapse on its own" the date is the real one. It is
        # NOT a promise that the session lasts that long -- a sign-out
        # elsewhere ends it early and leaves the jar untouched -- which is why
        # every tool still measures instead of reading this field.
        "expiry_is_authoritative": True,
    }


def _supporting(facts: dict[str, Any]) -> list[dict[str, Any]]:
    """Render ``JSESSIONID`` as the shared shape's ``supporting`` list.

    One entry, because there is exactly one. It is not a second credential:
    it carries no authority and cannot sign anything in. What it governs is
    whether the identity call can be MADE -- LinkedIn's own web app copies
    its value into the ``csrf-token`` header and the endpoint will not answer
    without one -- so it belongs beside the credential rather than inside it.
    """
    present = bool(facts.get("present"))
    dated = present and facts.get("expires_at") is not None
    entry: dict[str, Any] = {
        "name": CSRF_COOKIE,
        "role": "csrf",
        "present": present,
        "expires_at": facts.get("expires_at") if dated else None,
        "expires_in_days": facts.get("expires_in_days") if dated else None,
        "expired": facts.get("expired") if dated else None,
    }
    note = facts.get("note")
    if note:
        entry["note"] = note
    return [entry]


def _renewal(credential: dict[str, Any]) -> dict[str, Any]:
    """Why no ``linkedin_reauth`` exists, and WHEN the operator must sign in.

    The three sibling servers in this family were ruled on the same day and
    two of them DO ship a silent renew, so "there isn't one here" is a fact a
    caller needs stated rather than a gap it has to notice. Stating it in the
    result rather than only in a design note is the difference between a
    caller reporting the boundary and a caller hunting for a tool that was
    never built.

    ``session_lapses_at`` is the second half of that, and it answers a
    DIFFERENT question from ``credential.expires_at``. The credential's date
    says when that cookie dies. This one says when the SESSION dies -- the
    point past which no silent renew can help and the operator signs in by
    hand. Across four servers those are not the same number and can differ by
    orders of magnitude: naukri's ``nauk_at`` was measured live at +0.02 days
    while the server was silently re-minting it from a refresh cookie good for
    +188. A client comparing ``expires_at`` across the family would read that
    server as half an hour from death and this one as a year of headroom, when
    the honest comparison is 188 days against 364.

    Here the two dates COINCIDE, and that is a finding about LinkedIn rather
    than a field left unfilled: one credential layer, no refresh token beside
    it, nothing for a renew to refresh. So the moment ``li_at`` lapses is the
    moment the sign-in has to be done again by hand.
    ``session_lapses_source`` says exactly that, naming the credential that
    governs -- and when there is no date, why there is none.

    ``uses_browser`` is ``None`` here, and the reason is the same
    three-valued discipline this module applies to ``authenticated``. There is
    no renewal mechanism on this platform to characterise, so a ``False``
    would assert something about a thing that does not exist: "a renew exists
    and happens not to need a browser". Absence of a mechanism is not a
    mechanism that costs nothing, and the two servers in this family that DO
    ship a reauth both drive a browser -- which is exactly the cost the field
    was added to stop "silent renew" from hiding.

    ``mechanism`` therefore answers in its own words rather than pointing at
    ``why``. A caller comparing ``mechanism`` across four servers deserves a
    straight answer from each without following a cross-reference.
    """
    lapses_at = credential.get("expires_at")
    lapses_in_days = credential.get("expires_in_days")

    if lapses_at is None:
        # Null, never a zero and never a False. "No date is available" and
        # "the session ends now" are opposite readings of the same field, and
        # a zero would be read as the second one.
        source = (
            f"{SESSION_COOKIE} governs, and nothing else can: with one "
            "credential layer and no refresh token there is no other expiry "
            "that could stand in for it. No date is available here -- "
            + str(credential.get("expiry_source"))
        )
    else:
        source = (
            f"{SESSION_COOKIE}, and it governs ALONE. Because no silent renew "
            "exists on this platform, nothing can carry the session past the "
            "date the cookie itself carries, so this is EQUAL to "
            "credential.expires_at rather than derived from something else. "
            "That equality is a fact about LinkedIn, not a placeholder: on a "
            "server that can re-mint its credential the two dates come apart, "
            "and this is the one to compare across servers."
        )

    return {
        "silent_renew_available": False,
        "tool": None,
        # THE ABSENCE, MADE READABLE WITHOUT READING SOURCE. Three sibling
        # servers ship a reauth and two do not, and until 2026-08-25 a caller
        # could not tell a PRINCIPLED absence from a missing feature -- both
        # look like a tool that is not in the list. The reasoning was already
        # here in `why`, but prose is not something a client can branch on,
        # and "is there a reauth" is exactly the question a client asks when
        # a session lapses.
        #
        # reauth_absence_is_deliberate is the load-bearing one. A bare false
        # on silent_renew_available invites somebody to ship the decoy reauth
        # next quarter -- a tool that calls login and reports success, which
        # is worse than no tool because it implies a refresh happened.
        "reauth_tool": None,
        "reauth_absence_is_deliberate": True,
        "call_instead": "linkedin_login",
        "why": (
            "there is one credential layer here, so there is nothing a renew "
            f"could refresh. {SESSION_COOKIE} is read live out of the Chrome "
            "profile on every call -- this server keeps no cached copy that "
            "could go stale independently of the profile -- and LinkedIn "
            "issues no refresh token beside it. A linkedin_reauth would "
            "therefore be linkedin_login wearing a different name, so "
            "it is deliberately not shipped. Recovery is "
            "linkedin_login: it opens a window and waits for the "
            "operator to sign in himself, and this server never sees, types, "
            "stores or transmits a password."
        ),
        # The date past which no silent renew can help and the operator must
        # sign in by hand. Same route as the credential's own expiry, so it is
        # populated on the browserless path too and null when the jar could
        # not be read.
        "session_lapses_at": lapses_at,
        "session_lapses_in_days": lapses_in_days,
        "session_lapses_source": source,
        # None, not False. False would characterise a renewal that does not
        # exist. See the docstring above.
        "uses_browser": None,
        "mechanism": (
            "none -- there is no renewal mechanism here to describe, which is "
            "why uses_browser is null rather than false. Recovery is not a "
            "renewal at all: linkedin_login opens a real Chrome "
            "window and waits for the operator to sign in with his own hands. "
            "That is a HUMAN action, not a background one -- it cannot be "
            "scheduled, it cannot run while he is away from the machine, and "
            "this server never sees, types, stores or transmits the password "
            "he types into that window. The sign-in it replaces took him a "
            "full day to establish."
        ),
    }


def _durability(mode: str) -> dict[str, Any]:
    """Where the session is kept and what it survives. Shared by both paths."""
    from linkedin_server.config import CHROME_PROFILE, display

    return {
        # Relativised rather than deleted. This is the one field that answers
        # "where does my session actually live", and it is shared by BOTH the
        # live and the offline session result, so it is rendered once here.
        "stored_in": display(CHROME_PROFILE) if mode == "launch" else (
            "the browser this server is attached to, not a profile it owns"
        ),
        "survives_server_restart": mode == "launch",
        "survives_machine_reboot": mode == "launch",
        "why": (
            "the session lives in an on-disk Chrome profile, not in this "
            "process, so stopping the server or rebooting the machine "
            "leaves it exactly where it was. What ends it is LinkedIn "
            "expiring it, a sign-out, or the profile directory being "
            "deleted."
            if mode == "launch"
            else
            "in attach mode the session belongs to the browser the "
            "operator started. It lasts as long as that browser's own "
            "profile does, and this server neither owns nor preserves it."
        ),
        "measured_here": (
            "LinkedIn's own year-long cookies in this profile carry a "
            "365-day expiry (issued 2026-08-21, expiring 2027-08-21). "
            "The li_at figure above is read live from the jar and is the "
            "only one that governs the login."
        ),
    }


#: Said in both results, in the same words, because it is the one sentence
#: this whole module exists to enforce.
COOKIE_IS_NOT_A_SESSION = (
    "a cookie in the jar is NOT a session. li_at being present and unexpired "
    "means the login has not lapsed on its own; it does not mean LinkedIn "
    "still honours it. Only the live identity call establishes that."
)

#: What happens when the session does lapse, and the way back, BY NAME.
#: Rendered once because both paths say it and a reader comparing two results
#: should never have to wonder whether two spellings mean two things.
ON_EXPIRY = (
    "tools report 'not_authenticated' with the reason, never an empty result. "
    "Recover by calling linkedin_login and signing in yourself in the "
    "window it opens."
)


async def session_info(page: Any) -> dict[str, Any]:
    """Report the live session's state and how long it has left.

    Runs the ordinary identity measurement first (so ``authenticated`` here
    means exactly what it means everywhere else in this server), then reads
    the cookie jar for expiry dates. Cookie values are never returned.

    Two facts, two fields, never blurred into one: ``authenticated`` is the
    round-trip's verdict, and ``live_check`` says whether that round-trip
    actually happened. :func:`session_info_offline` reports the same shape
    when no browser could be started, with ``authenticated`` null rather than
    a cookie's presence quietly promoted into a verdict.

    The shape is the family's shared auth-lifecycle one: ``credential`` is
    the thing that authenticates (``li_at``), ``supporting`` is everything
    that merely governs whether the question can be PUT (``JSESSIONID``), and
    ``renewal`` says whether a silent renew exists here. It does not, and the
    field says why rather than leaving a caller to hunt for a tool that was
    never built.
    """
    status = await check_auth(page, corroborate=True)

    records = await _cookie_records(page)
    by_name = {c.get("name", ""): c for c in records}

    from linkedin_server.browser import BROWSER

    authenticated = status.get("authenticated")
    live_check: dict[str, Any] = {
        "attempted": True,
        "completed": authenticated is not None,
        "endpoint": AUTH_ENDPOINT_NOTE,
    }
    if authenticated is None:
        live_check["why_not"] = str(
            status.get("reason")
            or "the identity endpoint returned neither an identity nor a refusal."
        )
    live_check["what_it_means"] = (
        "the identity endpoint was asked and answered, so 'authenticated' "
        "above is a measurement"
        if authenticated is not None
        else
        "the identity endpoint was asked and did not answer either way, so "
        "'authenticated' is null rather than guessed. A null is not a 'no'."
    )

    # Built before the payload rather than inline: _renewal derives the
    # session's own lapse date FROM this block, so the two can never disagree
    # about a date they are both reporting.
    credential = _credential(
        _cookie_expiry(by_name.get(SESSION_COOKIE)),
        expiry_source=LIVE_EXPIRY_SOURCE,
    )

    out: dict[str, Any] = {
        "server": SERVER_ID,
        "authenticated": authenticated,
        "checked_against": status.get("checked_against"),
        "live_check": live_check,
        "credential": credential,
        "supporting": _supporting(_cookie_expiry(by_name.get(CSRF_COOKIE))),
        "credential_source": "the live browser's own cookie jar",
        "browser_mode": BROWSER.mode,
        "durability": _durability(BROWSER.mode),
        "renewal": _renewal(credential),
        "on_expiry": ON_EXPIRY,
    }

    for key in ("member", "public_identifier", "profile", "reason", "http_status"):
        if key in status:
            out[key] = status[key]
    return out


def session_info_offline(
    profile_dir: Any,
    *,
    mode: str,
    why_no_live_check: str,
    attempted: bool = False,
) -> dict[str, Any]:
    """Report what the ON-DISK profile says, with no browser involved at all.

    This is the answer to "did my session survive?" on the day the browser is
    the thing that is broken -- which is exactly when the question is worth
    asking, and exactly when the ordinary path cannot answer it. The expiry
    dates live in the profile's own SQLite cookie jar, so they are read from
    there (see ``cookie_jar.py``: a COPY is read, the live file is never
    opened, and no cookie value is ever fetched).

    What it deliberately does NOT do is call the login authenticated.
    ``authenticated`` is null here and stays null. Three login bugs in this
    family of servers came from substituting "a session cookie exists" for "a
    session works", the two are indistinguishable from the jar, and a
    year-long li_at sitting in a profile whose session LinkedIn revoked this
    morning looks exactly like a healthy one. So the jar facts are reported
    as jar facts, under their own labels, next to a live_check block that
    says in plain words that the verdict could not be obtained and why.

    Never raises. A jar that cannot be read is reported in
    ``credential_source`` alongside the browser's own failure, because "both
    routes failed, here is each reason" is more use than either error on its
    own.
    """
    from linkedin_server import cookie_jar
    from linkedin_server.config import scrub

    session_cookie: dict[str, Any] = {"present": False}
    csrf_cookie: dict[str, Any] = {"present": False}
    jar_error: Optional[str] = None
    try:
        records = cookie_jar.read_jar(profile_dir, [SESSION_COOKIE, CSRF_COOKIE])
        by_name = {r.get("name", ""): r for r in records}
        session_cookie = _cookie_expiry(by_name.get(SESSION_COOKIE))
        csrf_cookie = _cookie_expiry(by_name.get(CSRF_COOKIE))
    except cookie_jar.CookieJarUnavailableError as exc:
        # cookie_jar builds its messages as f"...{profile_dir}..." so the path
        # is INSIDE the prose, where renaming a field cannot reach it.
        jar_error = scrub(str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        jar_error = scrub(f"{type(exc).__name__}: {exc}")

    # Same reason as on the live path: _renewal reads its lapse date out of
    # this block, so one route produces both and they cannot drift apart.
    credential = _credential(
        session_cookie,
        expiry_source=DISK_EXPIRY_SOURCE,
        unreadable=jar_error,
    )

    out: dict[str, Any] = {
        "server": SERVER_ID,
        "authenticated": None,
        "checked_against": AUTH_ENDPOINT_NOTE,
        "live_check": {
            # "I tried and the browser is broken" and "you asked me not to
            # try" are different facts about the same null, and the operator
            # acts differently on each. They do not share a field.
            "attempted": attempted,
            "completed": False,
            "endpoint": AUTH_ENDPOINT_NOTE,
            "why_not": why_no_live_check,
            "what_it_means": (
                "'authenticated' is null because the live identity call could "
                "not be made, NOT because LinkedIn said no. The cookie facts "
                "below are the only thing measured here, and "
                + COOKIE_IS_NOT_A_SESSION
            ),
        },
        "credential": credential,
        "supporting": _supporting(csrf_cookie),
        "credential_source": (
            f"the profile's on-disk cookie jar, read without launching a "
            f"browser -- and it could not be read: {jar_error}"
            if jar_error
            else
            "the profile's on-disk cookie jar, read without launching a "
            "browser (a copy is read; no cookie value is ever fetched)"
        ),
        "browser_mode": mode,
        "durability": _durability(mode),
        "renewal": _renewal(credential),
        "on_expiry": ON_EXPIRY,
    }
    if jar_error:
        out["jar_error"] = jar_error
    return out


# ---------------------------------------------------------------------------
# Ending the LOCAL session -- the one destructive thing in this package
# ---------------------------------------------------------------------------

#: What a confirmed logout takes away, worded ONCE so the preview a caller
#: reads and the result he gets afterwards cannot drift into two claims.
#:
#: The jar file, not the profile directory. LinkedIn's session IS one row of
#: that jar, so erasing the jar ends the session; erasing the whole profile
#: would also take history, preferences and every other site's state, which
#: nobody asked to lose. The journal / WAL / SHM siblings go with it because
#: sqlite would otherwise replay a journal over a jar that is no longer there.
LOGOUT_SCOPE = (
    "the Chrome profile's on-disk cookie jar at Default/Network/Cookies, "
    "together with any -journal / -wal / -shm sibling beside it. Every cookie "
    "in that jar goes, which in this profile means the LinkedIn session and "
    "nothing else -- the profile exists for this server alone. The profile "
    "directory itself stays where it is."
)

#: What the operator loses, in the terms he cares about rather than in files.
LOGOUT_WHAT_IS_LOST = (
    "the signed-in LinkedIn session in this profile. It took a full day to "
    "establish, it is the only reason no tool here asks for a password, and "
    "there is no copy of it anywhere else on this machine."
)

#: The way back, BY NAME.
LOGOUT_RECOVER_BY = "linkedin_login"

#: Said on every outcome. A logout that quietly implied it had signed the
#: operator out of LinkedIn would be describing something this server has no
#: code path for, and he would act on it.
LOGOUT_IS_LOCAL_ONLY = (
    "nothing here reaches LinkedIn. No request is issued and no session is "
    "ended on LinkedIn's side; the account is untouched and any other browser "
    "signed in to it stays signed in. What lapses is purely local."
)


def _logout_targets(profile_dir: Any) -> list[Any]:
    """The exact files a confirmed logout erases, in the order it erases them.

    Pure path arithmetic -- it stats nothing and opens nothing, which is what
    lets the unconfirmed preview name them without touching the profile at
    all.
    """
    from linkedin_server import cookie_jar

    jar = Path(profile_dir).joinpath(*cookie_jar.JAR_RELPATH)
    return [jar] + [
        jar.with_name(jar.name + suffix)
        for suffix in cookie_jar.JAR_SIBLING_SUFFIXES
    ]


def _erase(path: Any) -> bool:
    """Erase one file. True if it was there, False if it never was.

    A named function rather than an inline unlink, so a test can replace it
    with a trap and prove the unconfirmed path never REACHES it. "Nothing
    changed on disk" is the weaker claim; "the erasing step was never
    entered" is the one worth having for a tool this expensive, and only a
    seam can carry it.
    """
    try:
        Path(path).unlink()
        return True
    except FileNotFoundError:
        return False


def logout(profile_dir: Any, *, confirm: bool = False) -> dict[str, Any]:
    """End the LOCAL session by erasing this profile's cookie jar.

    Args:
        profile_dir: the Chrome user-data dir holding the session.
        confirm: False -- the default -- performs NOTHING. No file is opened,
            no file is stat-ed, no browser starts, the profile is not read.
            The result carries a ``preview`` naming what a confirmed call
            would take and what it would cost. True erases the jar.

    Returns:
        The family's shared logout shape. ``authenticated`` is ``false`` ONLY
        where the credential is provably gone, which is what makes that false
        provable rather than measured; on every other outcome -- an
        unconfirmed call, a locked profile, a failed erase -- the credential
        is still sitting there, so ``authenticated`` is ``null`` with the
        reason, exactly as it is everywhere else in this module. A false
        nobody could act on is worse than a null somebody can.

    Never raises. Not for a missing profile, not for a locked one, not for a
    file the OS refuses to give up: each of those comes back as ``cleared``
    false carrying its own reason.
    """
    from linkedin_server import profile_lock
    from linkedin_server.config import display, scrub

    targets = _logout_targets(profile_dir)
    named = [display(target) for target in targets]

    if not confirm:
        return {
            "cleared": False,
            "scope": LOGOUT_SCOPE,
            # Not false: nothing was taken, so the session is exactly as live
            # (or as dead) as it was a moment ago, and this call did not ask.
            "authenticated": None,
            "reason": (
                "nothing was done. confirm was not given, so this call read "
                "no file, erased no file and started no browser."
            ),
            "what_is_lost": "nothing -- this was a preview.",
            "recover_by": LOGOUT_RECOVER_BY,
            "preview": {
                "would_erase": named,
                "would_lose": LOGOUT_WHAT_IS_LOST,
                "cost_to_re_establish": (
                    "a full day. That is what the sign-in in this profile "
                    "took the operator, and it is the reason this tool asks "
                    "twice."
                ),
                "recovery_is_by_hand": (
                    "there is no automated way back. Getting in again means "
                    f"{LOGOUT_RECOVER_BY} and a sign-in the operator performs "
                    "himself in the window it opens -- this server never "
                    "sees, types, stores or transmits a password."
                ),
                "linkedin_side": LOGOUT_IS_LOCAL_ONLY,
                "to_proceed": "call linkedin_logout(confirm=True).",
            },
        }

    holder = profile_lock.live_holder()
    if holder is not None:
        return {
            "cleared": False,
            "scope": LOGOUT_SCOPE,
            "authenticated": None,
            "reason": (
                f"refused: PID {holder} holds the cross-process profile lock, "
                "so a browser is on this profile right now. Erasing a jar out "
                "from under a live Chromium is how a profile gets corrupted, "
                "and a corrupted profile costs the same day this tool is "
                "asking about. Nothing was touched. Stop that process (or "
                "let this server's own browser close on its idle timer) and "
                "call again."
            ),
            "what_is_lost": "nothing -- the erase did not run.",
            "recover_by": LOGOUT_RECOVER_BY,
            "holder_pid": holder,
        }

    erased: list[str] = []
    failures: list[str] = []
    for target, name in zip(targets, named):
        try:
            if _erase(target):
                erased.append(name)
        except Exception as exc:
            failures.append(f"{name}: {scrub(f'{type(exc).__name__}: {exc}')}")

    if failures:
        return {
            "cleared": bool(erased),
            "scope": LOGOUT_SCOPE,
            "authenticated": None,
            "reason": (
                "the erase did not finish, so whether a usable credential is "
                "left cannot be stated from here: "
                + "; ".join(failures)
            ),
            "what_is_lost": (
                LOGOUT_WHAT_IS_LOST if erased else "nothing was taken."
            ),
            "recover_by": LOGOUT_RECOVER_BY,
            "erased": erased,
            "failed": failures,
            "linkedin_side": LOGOUT_IS_LOCAL_ONLY,
        }

    if not erased:
        return {
            "cleared": False,
            "scope": LOGOUT_SCOPE,
            "authenticated": None,
            "reason": (
                "there was no cookie jar at that path, so there was nothing "
                "to take. That is what a profile nobody has signed in to "
                "looks like -- it is not a failure, and it is not a verdict "
                "on a session either."
            ),
            "what_is_lost": "nothing -- there was nothing there.",
            "recover_by": LOGOUT_RECOVER_BY,
            "erased": [],
            "linkedin_side": LOGOUT_IS_LOCAL_ONLY,
        }

    return {
        "cleared": True,
        "scope": LOGOUT_SCOPE,
        # The one place in this module where a false is not a measurement,
        # and it is provable rather than guessed: li_at is gone, every tool
        # here authenticates with li_at and nothing else, so no authenticated
        # request can be made at all. There is no endpoint to ask.
        "authenticated": False,
        "reason": (
            f"{SESSION_COOKIE} is gone with the jar that held it. Every tool "
            "in this server authenticates with that cookie and nothing else, "
            "so no authenticated request can be made from here -- which is "
            "why this false is provable without asking LinkedIn."
        ),
        "what_is_lost": LOGOUT_WHAT_IS_LOST,
        "recover_by": LOGOUT_RECOVER_BY,
        "erased": erased,
        "linkedin_side": LOGOUT_IS_LOCAL_ONLY,
    }


def assert_not_authwall(final_url: str, *, surface: str) -> None:
    """Raise if a navigation landed on LinkedIn's signed-out wall.

    This is the auth check the data tools use, and it is free: they have to
    load the page anyway, and a redirect to ``/login`` IS an authenticated
    request being refused. Spending a separate identity call before every read
    would double this server's request rate to establish something the
    navigation already established.
    """
    if any(marker in (final_url or "") for marker in AUTHWALL_MARKERS):
        raise NotAuthenticatedError(
            f"loading the {surface} page landed on {final_url}, which is "
            "LinkedIn's signed-out wall -- there is no live session. Call "
            "linkedin_login and sign in yourself in the window it "
            "opens."
        )


async def require_auth(page: Any) -> dict[str, Any]:
    """Raise unless the session is measurably live. Returns the auth record."""
    status = await check_auth(page)
    if status.get("authenticated") is True:
        return status
    if status.get("authenticated") is False:
        raise NotAuthenticatedError(
            status.get("reason")
            or "no live LinkedIn session. Call linkedin_login first."
        )
    raise AuthUnknownError(
        status.get("reason")
        or "could not establish whether this session is signed in."
    )


# ---------------------------------------------------------------------------
# The login gate
# ---------------------------------------------------------------------------


async def login_via_browser(
    page: Any,
    *,
    wait_seconds: int = LOGIN_WAIT_S,
) -> dict[str, Any]:
    """Open LinkedIn's login page and wait for the operator to sign in himself.

    This server never sees, types, stores or transmits a credential. It opens
    the window; the human types into it; the persistent profile keeps the
    session afterwards so this is a one-time step.

    The window stays open until ``/voyager/api/me`` answers with an identity,
    the window is closed, or ``wait_seconds`` runs out. A ``li_at`` cookie
    appearing only causes the endpoint to be asked one more time.

    Returns:
        ``authenticated: true`` only when the endpoint said so. ``false`` with
        a ``reason`` on a timeout or a closed window. ``null`` when the state
        could not be determined at all.
    """
    started = time.time()

    already = await check_auth(page)
    if already.get("authenticated") is True:
        return {
            "authenticated": True,
            "already_signed_in": True,
            "elapsed_seconds": round(time.time() - started, 1),
            "checks_run": 1,
            **{k: v for k, v in already.items() if k != "authenticated"},
        }

    from linkedin_server.browser import BROWSER

    await BROWSER.goto(page, LOGIN_URL)
    logger.info(
        "login window open at %s -- waiting up to %ss for a confirmed sign-in",
        LOGIN_URL,
        wait_seconds,
    )

    # Starts at 1: the opening check above already spent a request, and
    # checks_run means "requests this wait put to LinkedIn", which is the
    # number that matters for rate discipline.
    checks = 1
    cookie_seen = False
    window_closed = False
    last_checked_cookies: Optional[dict[str, str]] = None
    last_check_at = 0.0
    last_status: dict[str, Any] = {}

    while True:
        if _page_is_dead(page):
            window_closed = True
            break

        try:
            cookies = await _cookies(page)
        except BrowserUnavailableError:
            window_closed = True
            break

        if SESSION_COOKIE in cookies:
            cookie_seen = True

        now = time.time()
        worth_asking = SESSION_COOKIE in cookies and (
            last_checked_cookies is None
            or cookies != last_checked_cookies
            or (now - last_check_at) >= LOGIN_RECHECK_S
        )
        if worth_asking and checks < LOGIN_MAX_CHECKS:
            last_checked_cookies = dict(cookies)
            last_check_at = now
            checks += 1
            last_status = await check_auth(page, warm=False)
            if last_status.get("authenticated") is True:
                return {
                    "authenticated": True,
                    "already_signed_in": False,
                    "elapsed_seconds": round(time.time() - started, 1),
                    "checks_run": checks,
                    "verified_by": AUTH_ENDPOINT_NOTE,
                    **{
                        k: v
                        for k, v in last_status.items()
                        if k not in {"authenticated", "reason"}
                    },
                }

        if time.time() - started >= wait_seconds:
            break
        await asyncio.sleep(LOGIN_POLL_S)

    elapsed = round(time.time() - started, 1)
    common = {
        "elapsed_seconds": elapsed,
        "checks_run": checks,
        "checked_against": AUTH_ENDPOINT_NOTE,
        "session_cookie_present": cookie_seen,
        "login_url": LOGIN_URL,
    }

    if last_status.get("authenticated") is None and last_status:
        return {
            "authenticated": None,
            "reason": (
                "could not determine whether the sign-in succeeded: "
                + str(last_status.get("reason", "the auth check gave no verdict"))
            ),
            **common,
        }

    if window_closed:
        reason = (
            "the browser window was closed before a signed-in session could be "
            "confirmed. If you did finish signing in, the profile kept it -- "
            "call linkedin_auth_status, or run this tool again and it will "
            "confirm in about a second."
        )
    else:
        reason = (
            f"no signed-in session appeared within {wait_seconds}s. The window "
            f"was open at {LOGIN_URL}; sign in there and call this tool again "
            "with a longer wait_seconds if you need more time."
        )
        if cookie_seen:
            reason += (
                " A li_at cookie was present, but the identity endpoint did not "
                "accept it, so it was not a live session."
            )

    return {"authenticated": False, "reason": reason, **common}


def _page_is_dead(page: Any) -> bool:
    try:
        return bool(page.is_closed())
    except Exception:
        return True
