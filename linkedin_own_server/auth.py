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

from linkedin_own_server.config import (
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
from linkedin_own_server.errors import (
    AuthUnknownError,
    BrowserUnavailableError,
    NotAuthenticatedError,
)

#: The cookie that carries a LinkedIn session. Its presence is a prompt to
#: ask the API, and that is the only role it has anywhere in this server.
SESSION_COOKIE = "li_at"
#: LinkedIn's web app sends this cookie's value back as the csrf-token header.
CSRF_COOKIE = "JSESSIONID"

#: Upper bound on how many times one login wait may spend a request.
LOGIN_MAX_CHECKS = 40

AUTH_ENDPOINT_NOTE = f"GET {ME_API}"


# ---------------------------------------------------------------------------
# The measurement
# ---------------------------------------------------------------------------


async def _cookies(page: Any) -> dict[str, str]:
    """Read the browser's cookie jar. Never logged, never persisted."""
    try:
        jar = await page.context.cookies("https://www.linkedin.com")
    except Exception as exc:
        raise BrowserUnavailableError(
            f"could not read the browser session: {type(exc).__name__}: {exc}"
        ) from exc
    return {c.get("name", ""): c.get("value", "") for c in jar or []}


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


async def check_auth(page: Any, *, corroborate: bool = False) -> dict[str, Any]:
    """Ask LinkedIn whether this session is signed in.

    Args:
        page: a live Playwright page from the persistent-profile context.
        corroborate: when the API answer is inconclusive, also load the feed
            and look at where it lands. Costs one page load, so tools that
            are mid-flow (the login wait) leave it off.

    Returns:
        A dict with ``authenticated`` (``True`` / ``False`` / ``None``),
        ``checked_against``, and a ``reason`` whenever the answer is not
        ``True``. Never raises for a plain signed-out session -- that is an
        answer, not an error.
    """
    cookies = await _cookies(page)
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
        return await _maybe_corroborate(page, result, corroborate)

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
    )


async def _maybe_corroborate(
    page: Any, result: dict[str, Any], corroborate: bool
) -> dict[str, Any]:
    """Second, independent read: does the feed bounce us to an auth wall?

    Only ever used to turn an UNKNOWN into a ``false``. It is never allowed to
    manufacture a ``true`` -- landing on the feed proves rather less than the
    identity endpoint answering, and this server does not upgrade a verdict on
    weaker evidence.
    """
    if not corroborate:
        return result

    from linkedin_own_server.browser import BROWSER

    try:
        final_url = await BROWSER.goto(page, FEED_URL)
    except Exception as exc:
        logger.info("corroborating navigation failed: %s: %s", type(exc).__name__, exc)
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

    from linkedin_own_server.browser import BROWSER

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
            last_status = await check_auth(page)
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
