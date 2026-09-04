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
from typing import Any, Optional

from linkedin_server import paths as _paths

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

SERVER_NAME = "linkedin"
SERVER_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

#: Repo root (the directory holding this package).
PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent

#: All local state lives under one gitignored directory.
STATE_DIR = Path(
    os.environ.get("LINKEDIN_STATE_DIR", str(REPO_ROOT / "_state"))
).resolve()

#: The persistent Chrome profile. This is the ONLY place the operator's
#: LinkedIn session is kept, it never leaves this machine, and this server
#: never copies cookies out of it into a file, a log or a tool result.
CHROME_PROFILE = Path(
    os.environ.get("LINKEDIN_PROFILE_DIR", str(STATE_DIR / "chrome-profile"))
).resolve()

#: THE ONLY DIRECTORY A FILE MAY BE UPLOADED FROM. Declared here, beside the
#: profile, because it is the same class of thing: a boundary that decides
#: what of this machine this server can reach.
#:
#: WHY A ROOT AT ALL, AND WHY IT IS THE WHOLE OF THE PROTECTION. Every other
#: act this server performs operates on something ALREADY ON THE PAGE -- a
#: control it found, a string he typed. An upload is the first one that takes
#: an arbitrary path from a caller and hands it to a browser, and a path with
#: no root can name a private key as easily as a photograph. The root turns
#: "any file on this machine" into "a file he put here on purpose", and
#: PUTTING IT HERE IS THE CONSENT that no string comparison can fake.
#:
#: NOT CREATED HERE, deliberately. ``uploads.resolve_upload_file`` refuses and
#: NAMES this directory when it is missing, so the answer to "where do I put
#: it" is in the refusal rather than in a directory that appeared by itself.
#: A guard that makes its own subject exist is a guard with a side effect.
UPLOAD_ROOT = Path(
    os.environ.get("LINKEDIN_UPLOAD_DIR", str(STATE_DIR / "uploads"))
).resolve()

# ---------------------------------------------------------------------------
# Rendering a path INTO a tool result
# ---------------------------------------------------------------------------

#: The anchor every displayed path is measured against, defined ONCE here so
#: that no call site can quietly pick a different one and produce two spellings
#: of the same directory in one payload.
#:
#: Absolute local paths do not belong in a tool result: they publish this
#: machine's directory layout into any transcript the result is pasted into,
#: and they are paid for in tokens on every response that carries one. The fix
#: is NOT to delete the field -- "where does my session actually live" is a
#: real question these fields answer, and a null trades a leak for a field that
#: answers nothing. See ``paths.py`` (vendored from jobcore) for the three
#: rendering forms and why the third one exists.
DISPLAY_ANCHOR = REPO_ROOT


def display(raw: Any) -> Optional[str]:
    """Render one path for a tool result: anchor-relative, ``~/...``, or tail."""
    return _paths.display_path(raw, anchor=DISPLAY_ANCHOR)


def known_paths() -> tuple[str, ...]:
    """The absolute paths this server knows it may have baked into a message.

    Read fresh on every call rather than frozen into a constant, because the
    profile directory is overridable by environment variable and a test that
    points it somewhere else must get that directory scrubbed too.

    This is the deliberately SHORT list that :func:`scrub` is allowed to
    substitute. It is not "every path-shaped thing in the text": see
    ``paths.relativise_known`` for why a heuristic scrubber does more damage
    than the leak it was written for.
    """
    out: list[str] = []
    # UPLOAD_ROOT IS ON THIS LIST BECAUSE IT IS OVERRIDABLE. Under the default
    # it sits inside STATE_DIR and would be scrubbed by that entry anyway;
    # pointed elsewhere by LINKEDIN_UPLOAD_DIR it would not be, and an upload
    # refusal quotes the root it measured against. A directory a person chose
    # for their own files is exactly the kind of path that carries their name.
    for raw in (CHROME_PROFILE, UPLOAD_ROOT, STATE_DIR, REPO_ROOT, PACKAGE_DIR):
        text = str(raw)
        out.append(text)
        # ...and the same path as REPR would spell it. Measured 2026-08-22:
        # OSError.__str__ renders its filename through repr(), so
        #     OSError(2, "...", r"D:")
        # stringifies with DOUBLED backslashes -- "D:\a\b" -- and an exact
        # substitution for the single-backslash form finds nothing. The regex
        # second opinion in tests/test_path_hygiene.py caught this after the
        # path-string check had already declared the payload clean, which is
        # the whole argument for keeping two detectors. On posix the two forms
        # are identical and this adds nothing.
        escaped = text.replace("\\", "\\\\")
        if escaped != text:
            out.append(escaped)
    return tuple(out)


def scrub(text: Any) -> Any:
    """Replace this server's own known paths wherever they sit inside prose.

    Renaming a field does not help when the path was interpolated into a
    sentence. Several messages in this package are built as
    ``f"...{path}...{exc}"`` -- and an OSError stringifies with the filename it
    failed on -- so a path reaches a caller through error text from call sites
    that render no path field of their own. Non-strings pass through untouched,
    so this is safe to map over a whole payload.
    """
    return _paths.relativise_known(text, known=known_paths(), render=display)


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

#: His own message surface. NOT a list url despite how it reads: LinkedIn
#: redirects it into one specific conversation thread of its own choosing,
#: measured twice. linkedin_open_messaging is named for that rather than for
#: what the path suggests.
MESSAGING_URL = f"{BASE_URL}/messaging/"

LOGIN_URL = f"{BASE_URL}/login"

#: Signed-out landing pages. A final url matching any of these means "not
#: signed in", whatever the cookie jar happens to contain.
AUTHWALL_MARKERS = ("/login", "/authwall", "/uas/login", "/checkpoint/")

# ---------------------------------------------------------------------------
# How the browser is launched
# ---------------------------------------------------------------------------

#: The DevTools port the launched browser listens on, so the secondary
#: recovery path (``cdp_bridge``) can attach to it. Distinct from the sibling
#: Naukri server's 9223 on purpose: two servers on one port is a collision,
#: and the second one to start would silently get no port at all.
CDP_PORT = int(os.environ.get("LINKEDIN_CDP_PORT", "9224"))

#: Literal ``127.0.0.1``, never ``localhost``. Measured on this machine:
#: Chrome binds the DevTools port on IPv4 only, so ``localhost`` resolves to
#: ``[::1]`` first, is refused, and falls back -- 2085 ms against 35 ms.
CDP_HOST = os.environ.get("LINKEDIN_CDP_HOST", "127.0.0.1")

#: Set ``LINKEDIN_CDP_ATTACH=1`` to run in ATTACH mode: instead of
#: launching its own browser, this server connects to a Chrome the operator
#: started himself with ``--remote-debugging-port``. Recovery path only --
#: see ``cdp_bridge.py`` for what it costs and what it requires.
CDP_ATTACH = os.environ.get("LINKEDIN_CDP_ATTACH", "").strip().lower() in {
    "1",
    "true",
    "yes",
}

#: The COMPLETE list of Chromium command-line flags this server passes. It is
#: two entries and a test asserts it stays exactly these two, because this is
#: the file where a "just one more flag" fix would land.
#:
#: ``--disable-blink-features=AutomationControlled`` turns off one Blink
#: feature: the one that sets ``navigator.webdriver = true``. Without it the
#: browser announces at every page load that it is automated, and LinkedIn
#: refuses to complete a sign-in. It is what the sibling Naukri server has
#: run for months (``naukri_server/browser.py``). It changes ONE boolean; it
#: does not spoof a user agent, a platform, a canvas, a font list or a
#: timezone, and this server does none of those things anywhere.
#:
#: ``--remote-debugging-port`` opens the DevTools port described above.
LAUNCH_ARGS: tuple[str, ...] = (
    "--disable-blink-features=AutomationControlled",
    f"--remote-debugging-port={CDP_PORT}",
)

# ---------------------------------------------------------------------------
# Rate discipline
# ---------------------------------------------------------------------------

#: Minimum seconds between two navigations, enforced globally across tools.
#: This is spacing, not disguise: it exists so a burst of tool calls cannot
#: turn into a burst of page loads, and it is applied uniformly rather than
#: jittered to look like anything.
MIN_NAVIGATION_INTERVAL_S = float(
    os.environ.get("LINKEDIN_MIN_INTERVAL_S", "3.0")
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
IDLE_CLOSE_S = float(os.environ.get("LINKEDIN_IDLE_CLOSE_S", "300"))

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

logger = logging.getLogger("linkedin")
if not logger.handlers:  # pragma: no cover - wiring
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
logger.setLevel(os.environ.get("LINKEDIN_LOG_LEVEL", "INFO"))
#: stdio transport: logs MUST NOT go to stdout or they corrupt the protocol.
logger.propagate = False
