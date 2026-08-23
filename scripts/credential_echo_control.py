"""A LEAKING build of this server's auth results, for showing the leak tests
can fail.

WHY THIS FILE IS IN THE REPO
----------------------------
Every "no cookie value reaches a tool result" assertion in this package was an
exact substring hunt::

    assert PLANTED_SECRET not in json.dumps(result)

That shape has a known blind spot, and a sibling server in this family was
caught by it: the marker it hunted was plaintext, the credential it guarded
was base64url, and so a result that echoed the ENTIRE credential in an encoded
form passed the check clean. A guard that cannot see the CLASS of thing it
guards against is not a guard -- the same sentence the fixture privacy check
in ``tests/test_sdui_surfaces_fixture.py`` already carries, learned there the
same way.

This pytest plugin makes that concrete. It wraps the five result-producing
auth entry points, reads the credential the TEST ITSELF planted (from the
page's cookie jar on the live paths, from the synthetic sqlite jar on the
offline ones -- so it echoes the real thing, not a constant of its own), and
puts it back into the payload under one chosen transform. Every transform
below is a way a credential has actually escaped a real program: a "safe"
truncated fingerprint, a debug blob, a url parameter, a value split across two
display fields, a log line nobody read.

The requirement is simple and total: **the leak tests must go RED under every
single transform.** A transform that leaves them green is a leak this suite
would ship.

HOW TO RUN IT
-------------
    LINKEDIN_LEAK_TRANSFORM=b64 PYTHONPATH=scripts \
        pytest -p credential_echo_control tests/test_auth.py

    # PowerShell
    $env:LINKEDIN_LEAK_TRANSFORM="b64"; $env:PYTHONPATH="scripts"
    venv/Scripts/python -m pytest -p credential_echo_control tests/test_auth.py

``scripts/leak_matrix.py`` runs the whole grid and prints the table. Its two
measured runs -- the exact-substring build and the transform-aware one -- are
in ``_audit/2026-08-23-build-linkedin.md``.
"""

from __future__ import annotations

import base64
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

#: Every way the wrapped payload can carry the credential back out.
TRANSFORMS = (
    "verbatim",
    "prefix12",
    "b64",
    "b64url_nopad",
    "hex",
    "percent",
    "split",
    "repr_escaped",
    "in_log",
)

_LOG = logging.getLogger("linkedin_server.auth")


def render(secret: str, transform: str) -> Any:
    """One credential, rendered the way the chosen leak would render it."""
    raw = secret.encode("utf-8")
    if transform == "verbatim":
        return secret
    if transform == "prefix12":
        # The "safe fingerprint" that is not safe: twelve characters of a
        # credential is twelve characters of a credential.
        return secret[:12] + "..."
    if transform == "b64":
        return base64.b64encode(raw).decode("ascii")
    if transform == "b64url_nopad":
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    if transform == "hex":
        return raw.hex()
    if transform == "percent":
        return quote(secret, safe="")
    if transform == "split":
        half = len(secret) // 2
        return [secret[:half], secret[half:]]
    if transform == "repr_escaped":
        # An OSError stringifies its filename through repr(). That rendering
        # already defeated an exact-substring PATH check in this repo (see
        # config.known_paths); this drives it at a credential instead.
        return str(OSError(2, "no such file", secret))
    raise AssertionError("unknown transform " + repr(transform))


def inject(payload: Any, secret: Optional[str], transform: str) -> Any:
    """Put the credential back into a result the way a leaking build would."""
    if not secret or not isinstance(payload, dict):
        return payload
    if transform == "in_log":
        # Not in the result at all. Only in a log record -- which is exactly
        # where a leak hides from a test that reads only the return value.
        _LOG.debug("session cookie for this profile is %s", secret)
        return payload
    rendered = render(secret, transform)
    credential = payload.get("credential")
    if isinstance(credential, dict):
        # Inside the credential block, where a redaction bug would live.
        credential["fingerprint"] = rendered
    else:
        payload["fingerprint"] = rendered
    return payload


async def _secret_from_page(page: Any) -> Optional[str]:
    try:
        rows = await page.context.cookies()
    except Exception:
        return None
    for row in rows or []:
        if row.get("name") == "li_at":
            return row.get("value")
    return None


def _secret_from_profile(profile_dir: Any) -> Optional[str]:
    """Read the planted value straight out of the test's synthetic jar.

    Reading the jar rather than carrying a constant is the point: the control
    echoes whatever the test planted, so a test that changes its marker keeps
    the control honest without anyone editing this file.
    """
    try:
        jar = Path(profile_dir) / "Default" / "Network" / "Cookies"
        if not jar.is_file():
            return None
        con = sqlite3.connect(str(jar))
        try:
            row = con.execute(
                "SELECT value FROM cookies WHERE name = 'li_at' LIMIT 1"
            ).fetchone()
        finally:
            con.close()
        return row[0] if row else None
    except Exception:
        return None


def pytest_sessionstart(session):
    transform = os.environ.get("LINKEDIN_LEAK_TRANSFORM", "verbatim")
    assert transform in TRANSFORMS, "unknown transform " + repr(transform)

    from linkedin_server import auth, server

    real_check = auth.check_auth
    real_live = auth.session_info
    real_offline = auth.session_info_offline
    real_login = auth.login_via_browser
    real_logout = auth.logout

    async def check_auth(page, *args, **kwargs):
        out = await real_check(page, *args, **kwargs)
        return inject(out, await _secret_from_page(page), transform)

    async def session_info(page, *args, **kwargs):
        out = await real_live(page, *args, **kwargs)
        return inject(out, await _secret_from_page(page), transform)

    def session_info_offline(profile_dir, *args, **kwargs):
        out = real_offline(profile_dir, *args, **kwargs)
        return inject(out, _secret_from_profile(profile_dir), transform)

    async def login_via_browser(page, *args, **kwargs):
        out = await real_login(page, *args, **kwargs)
        return inject(out, await _secret_from_page(page), transform)

    def logout(profile_dir, *args, **kwargs):
        # Read the secret BEFORE the erase, or there is nothing left to leak.
        secret = _secret_from_profile(profile_dir)
        out = real_logout(profile_dir, *args, **kwargs)
        return inject(out, secret, transform)

    patched = (
        ("check_auth", check_auth),
        ("session_info", session_info),
        ("session_info_offline", session_info_offline),
        ("login_via_browser", login_via_browser),
        ("logout", logout),
    )
    for module in (auth, server):
        # server.py binds these names at import; patching auth alone would
        # leave every tool-level test running the honest build.
        for name, fn in patched:
            if hasattr(module, name):
                setattr(module, name, fn)

    print(
        "\n[credential_echo_control] every auth result now carries the "
        "planted li_at back out, rendered as " + repr(transform)
    )
