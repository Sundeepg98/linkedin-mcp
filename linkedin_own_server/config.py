"""Paths, timeouts, caps and the logger for the read-only LinkedIn reader.

Everything tunable lives here so the numbers that govern how often this server
touches LinkedIn are visible in one file rather than scattered through call
sites. The caps are deliberately small: this reads ONE human's own account,
by hand, one action at a time.

Nothing in this module reads or writes a credential. The persistent Chrome
profile is the only place a session lives, it stays on this machine, and it is
gitignored.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

SERVER_NAME = "linkedin-own"
SERVER_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

#: Repo root (the directory holding this package).
PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent

#: All local state lives under one gitignored directory.
STATE_DIR = Path(
    os.environ.get("LINKEDIN_OWN_STATE_DIR", str(REPO_ROOT / "_state"))
).resolve()

#: The persistent Chrome profile. This is the ONLY place the operator's
#: LinkedIn session is kept, it never leaves this machine, and this server
#: never copies cookies out of it into a file, a log or a tool result.
CHROME_PROFILE = Path(
    os.environ.get("LINKEDIN_OWN_PROFILE_DIR", str(STATE_DIR / "chrome-profile"))
).resolve()

# ---------------------------------------------------------------------------
# LinkedIn endpoints (read surfaces only -- see readonly.py for the guard)
# ---------------------------------------------------------------------------

BASE_URL = "https://www.linkedin.com"

#: The canonical "who am I" call LinkedIn's own web app makes on page load.
#: This is the request that decides whether we are signed in. A cookie never is.
ME_API = f"{BASE_URL}/voyager/api/me"

#: Corroborating measurement: the feed bounces signed-out visitors to an
#: auth wall, so the FINAL url after a navigation is a second, independent
#: read of the same question.
FEED_URL = f"{BASE_URL}/feed/"

LOGIN_URL = f"{BASE_URL}/login"

#: Signed-out landing pages. A final url matching any of these means "not
#: signed in", whatever the cookie jar happens to contain.
AUTHWALL_MARKERS = ("/login", "/authwall", "/uas/login", "/checkpoint/")

# ---------------------------------------------------------------------------
# Rate discipline
# ---------------------------------------------------------------------------

#: Minimum seconds between two navigations, enforced globally across tools.
#: This is spacing, not disguise: it exists so a burst of tool calls cannot
#: turn into a burst of page loads, and it is applied uniformly rather than
#: jittered to look like anything.
MIN_NAVIGATION_INTERVAL_S = float(
    os.environ.get("LINKEDIN_OWN_MIN_INTERVAL_S", "3.0")
)

#: A data tool performs ONE page load. There is no scroll loop, no "next
#: page" walk, no background refresh. Paging is the operator's call, one
#: deliberate tool call at a time (see the ``start`` argument on search).
#: The single exception is the profile reader, which loads a second page for
#: the full skills list when asked, and reports ``pages_loaded: 2`` when it
#: does. Nothing may exceed this ceiling.
MAX_NAVIGATIONS_PER_CALL = 2

#: Close the browser after this long with no tool call, releasing the profile
#: lock. A window left open for hours is a session left exposed for hours.
IDLE_CLOSE_S = float(os.environ.get("LINKEDIN_OWN_IDLE_CLOSE_S", "300"))

# ---------------------------------------------------------------------------
# Timeouts (milliseconds where Playwright wants ms)
# ---------------------------------------------------------------------------

NAV_TIMEOUT_MS = 45_000
#: How long to let the page's own XHRs settle after DOM content is ready.
#: One bounded wait, not a poll loop.
SETTLE_MS = 3_500
API_TIMEOUT_MS = 20_000

#: Default seconds the login window stays open waiting for a human.
LOGIN_WAIT_S = 300
#: How often the login wait looks at the browser (local, free).
LOGIN_POLL_S = 2.0
#: How often the login wait is willing to SPEND a request re-asking the API
#: when the cookie jar has not moved.
LOGIN_RECHECK_S = 10.0

# ---------------------------------------------------------------------------
# Result caps -- token efficiency is the governing constraint
# ---------------------------------------------------------------------------

DEFAULT_LIMIT = 25
MAX_LIMIT = 100
SEARCH_DEFAULT_LIMIT = 25
SEARCH_MAX_LIMIT = 50
NOTIFICATIONS_DEFAULT_LIMIT = 20
NOTIFICATIONS_MAX_LIMIT = 50

#: Free text (headlines, notification bodies) is trimmed to this many
#: characters. Never a raw DOM dump, never a full page.
MAX_TEXT_CHARS = 180

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("linkedin_own")
if not logger.handlers:  # pragma: no cover - wiring
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
logger.setLevel(os.environ.get("LINKEDIN_OWN_LOG_LEVEL", "INFO"))
#: stdio transport: logs MUST NOT go to stdout or they corrupt the protocol.
logger.propagate = False
