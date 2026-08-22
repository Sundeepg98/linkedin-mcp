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
                "session. Call linkedin_login_browser and sign in yourself in "
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
            "linkedin_login_browser and sign in yourself."
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
    """
    status = await check_auth(page, corroborate=True)

    records = await _cookie_records(page)
    by_name = {c.get("name", ""): c for c in records}

    session_cookie = _cookie_expiry(by_name.get(SESSION_COOKIE))
    session_cookie["name"] = SESSION_COOKIE

    csrf_cookie = _cookie_expiry(by_name.get(CSRF_COOKIE))
    csrf_cookie["name"] = CSRF_COOKIE

    from linkedin_server.browser import BROWSER

    authenticated = status.get("authenticated")
    out: dict[str, Any] = {
        "authenticated": authenticated,
        "checked_against": status.get("checked_against"),
        "live_check": {
            "attempted": True,
            "completed": authenticated is not None,
            "endpoint": AUTH_ENDPOINT_NOTE,
            "what_it_means": (
                "the identity endpoint was asked and answered, so "
                "'authenticated' above is a measurement"
                if authenticated is not None
                else
                "the identity endpoint was asked and did not answer either "
                "way, so 'authenticated' is null rather than guessed"
            ),
        },
        "cookie_source": "the live browser's own cookie jar",
        "session_cookie": session_cookie,
        "csrf_cookie": csrf_cookie,
        "browser_mode": BROWSER.mode,
        "durability": _durability(BROWSER.mode),
        "on_expiry": (
            "tools report 'not_authenticated' with the reason, never an empty "
            "result. Recover by calling linkedin_login_browser and signing in "
            "yourself in the window it opens."
        ),
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

    Never raises. A jar that cannot be read is reported in ``cookie_source``
    alongside the browser's own failure, because "both routes failed, here is
    each reason" is more use than either error on its own.
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

    session_cookie["name"] = SESSION_COOKIE
    csrf_cookie["name"] = CSRF_COOKIE

    out: dict[str, Any] = {
        "authenticated": None,
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
        "cookie_source": (
            f"the profile's on-disk cookie jar, read without launching a "
            f"browser -- and it could not be read: {jar_error}"
            if jar_error
            else
            "the profile's on-disk cookie jar, read without launching a "
            "browser (a copy is read; no cookie value is ever fetched)"
        ),
        "session_cookie": session_cookie,
        "csrf_cookie": csrf_cookie,
        "browser_mode": mode,
        "durability": _durability(mode),
        "on_expiry": (
            "tools report 'not_authenticated' with the reason, never an empty "
            "result. Recover by calling linkedin_login_browser and signing in "
            "yourself in the window it opens."
        ),
    }
    if jar_error:
        out["jar_error"] = jar_error
    return out


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
            "linkedin_login_browser and sign in yourself in the window it "
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
            or "no live LinkedIn session. Call linkedin_login_browser first."
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
