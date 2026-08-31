"""Is there actually a browser to launch? Asked before launching one.

Every tool in this server that reads LinkedIn drives a real Chromium. When
that Chromium is not on disk, Playwright raises a bare
``BrowserType.launch_persistent_context: Executable doesn't exist at <path>``
with an ASCII-art banner suggesting ``playwright install``. That traceback
reaches the operator's MCP client as an unhandled error, and it is one fact
short of being diagnosable -- which is not a hypothetical:

    On 2026-08-22 every tool in this server died at browser launch. The
    resolved path was ``C:\\Users\\<user>\\AppData\\Local\\ms-playwright\\
    chromium-1234\\chrome-win64\\chrome.exe``. The client read the traceback
    and concluded Playwright had been updated without re-running the browser
    download, and recommended ``playwright install chromium``. That was
    WRONG, and acting on it would have downloaded ~150 MB to a drive the
    operator had just had a space emergency over. ``chromium-1234`` was
    present the whole time -- at ``D:\\dev-cache\\ms-playwright\\`` -- because
    ``PLAYWRIGHT_BROWSERS_PATH`` points there. The variable is set in the
    operator's user environment, but the client spawned this stdio server
    passing only ``PYTHONUNBUFFERED``, so the child process never saw it and
    Playwright fell back to its default location.

The single fact that turns that wrong diagnosis into the right one is the
VALUE OF THE ENVIRONMENT VARIABLE, sitting next to the resolved path. A
message saying only "browser missing" leads straight back to the 150 MB
mistake. So every message this module produces carries BOTH, always, and
``tests/test_preflight.py`` fails if either one is dropped.

TWO CHECKS, because one cannot cover the ground:

* :func:`assert_ready` runs BEFORE the launch and asks Playwright itself
  where it will look (``chromium.executable_path``). Cheap -- the driver is
  already started at that point, so it costs no extra process -- and it runs
  before the profile lock is taken, so a missing browser never leaves the
  operator reading "the profile is locked" instead.

* :func:`translate_launch_failure` runs AFTER a failed launch and rewrites
  Playwright's own "Executable doesn't exist at X" into the same message,
  using the path PLAYWRIGHT named. This is not belt-and-braces; it covers
  ground the first check cannot. Measured on this machine 2026-08-22: a
  HEADLESS launch does not use ``executable_path`` at all, it uses
  ``chromium_headless_shell-1234\\chrome-headless-shell-win64\\
  chrome-headless-shell.exe`` -- a different binary, in a differently-named
  directory, whose path Playwright's Python API does not publish. Predicting
  it here would mean reimplementing Playwright's private on-disk layout, and
  a copy of someone else's layout rots silently the first time they rename a
  directory. So this module never guesses a path: it reports the one
  Playwright publishes, and otherwise lets Playwright resolve the path and
  translates the failure.

The second check is also what keeps the message clean. Playwright's error
carries a box-drawing banner, and this package logs through a
``StreamHandler`` that on a Windows console encodes cp1252 -- printing that
banner raises ``UnicodeEncodeError``, measured while writing this module.
Extracting only the path leaves nothing non-ASCII behind.

Nothing here launches a browser, opens a profile, or touches the network.
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional

from linkedin_server.errors import BrowserUnavailableError

#: The variable that decides where Playwright looks for browser binaries.
#: Unset, it falls back to a per-user default (``%LOCALAPPDATA%\\ms-playwright``
#: on Windows). This server does not read it to USE it -- Playwright does that
#: -- it reads it to REPORT it, because its value is half the diagnosis.
BROWSERS_PATH_ENV = "PLAYWRIGHT_BROWSERS_PATH"

#: The command that installs the browsers.
INSTALL_COMMAND = "playwright install chromium"

#: Playwright's own words when the binary is not where it looked. The path
#: follows on the same line; a banner follows on the next. Written tolerantly
#: around the apostrophe so a future release that types a curly one still
#: matches, since the alternative is silently falling back to a raw traceback.
_MISSING_EXECUTABLE = re.compile(
    r"Executable\s+doesn.?t\s+exist\s+at\s+(.+?)(?:\r?\n|$)"
)


def browsers_path_setting() -> Optional[str]:
    """The raw value of :data:`BROWSERS_PATH_ENV`, or ``None`` if unset.

    An empty or whitespace-only value counts as unset: Playwright ignores it
    and falls back, so reporting it as "set to ''" would describe the config
    rather than the behaviour.
    """
    raw = os.environ.get(BROWSERS_PATH_ENV)
    if raw is None or not raw.strip():
        return None
    return raw


def describe_browsers_path() -> str:
    """One clause naming what the environment variable is, for a message."""
    value = browsers_path_setting()
    if value is None:
        return (
            f"{BROWSERS_PATH_ENV} is unset in this server's own environment, "
            "so Playwright fell back to its default location"
        )
    return f"{BROWSERS_PATH_ENV} is set to {value}"


def missing_browser_message(resolved_path: str) -> str:
    """The one actionable line a missing browser produces.

    Carries the resolved path AND the environment variable's actual value.
    That pair is the whole point of this module; see the module docstring for
    the day it was needed.
    """
    value = browsers_path_setting()
    if value is None:
        mechanism = (
            f"A stdio MCP server inherits ONLY the variables its client "
            f"passes in that server's env block -- {BROWSERS_PATH_ENV} being "
            "set in your user environment does NOT reach it otherwise, so "
            "check that before assuming the browsers are missing."
        )
        fix = (
            f"if your browsers are installed elsewhere, add "
            f"{BROWSERS_PATH_ENV} to this server's env block in the client "
            f"config and restart the client; only if they are genuinely not "
            f"installed, run: {INSTALL_COMMAND}"
        )
    else:
        mechanism = (
            "That is where Playwright looked, so the browsers are not "
            "installed there (they may be installed somewhere else)."
        )
        fix = (
            f"run: {INSTALL_COMMAND}  -- with {BROWSERS_PATH_ENV}={value} "
            "set in the same shell, so it installs where this server looks"
        )
    return (
        f"No Playwright browser executable at {resolved_path}. "
        f"{describe_browsers_path()}. {mechanism} Fix: {fix}"
    )


def unresolvable_message(reason: str) -> str:
    """Message for the case where Playwright cannot even name a path."""
    return (
        f"Playwright could not say where its browser executable is "
        f"({reason}). {describe_browsers_path()}. Fix: check the playwright "
        f"install in this server's own environment, then run: "
        f"{INSTALL_COMMAND}"
    )


def check(playwright: Any, *, headless: bool) -> dict[str, Any]:
    """Ask Playwright where the browser is and whether it is there.

    Args:
        playwright: a STARTED Playwright instance. Nothing is launched.
        headless: whether the launch this precedes will be headless. It does
            not change what is checked -- it changes what the result is
            allowed to CLAIM, see ``verified_for_this_mode`` below.

    Returns a verdict rather than raising, so a diagnostic tool can report it
    without a browser having to work first:

    * ``ok`` -- the published executable is on disk.
    * ``resolved_path`` -- what Playwright says it will use, or ``None``.
    * ``browsers_path_env`` -- the variable's value, or ``None`` for unset.
    * ``verified_for_this_mode`` -- ``True`` headful, ``False`` headless.
      Playwright publishes ONE path and it is the headful binary; a headless
      launch uses a separate ``chrome-headless-shell`` executable whose path
      the Python API does not expose. Claiming this check covered a headless
      launch would be a check that cannot fail for the case it is asked
      about, so it says so instead and
      :func:`translate_launch_failure` is what covers that case.
    * ``message`` -- present only when something is wrong.
    """
    try:
        resolved = playwright.chromium.executable_path
    except Exception as exc:
        reason = f"{type(exc).__name__}: {exc}"
        return {
            "ok": False,
            "resolved_path": None,
            "exists": False,
            "browsers_path_env": browsers_path_setting(),
            "headless": headless,
            "verified_for_this_mode": False,
            "message": unresolvable_message(reason),
        }

    resolved = str(resolved)
    exists = os.path.isfile(resolved)
    verdict: dict[str, Any] = {
        "ok": exists,
        "resolved_path": resolved,
        "exists": exists,
        "browsers_path_env": browsers_path_setting(),
        "headless": headless,
        "verified_for_this_mode": bool(exists and not headless),
    }
    if not exists:
        verdict["message"] = missing_browser_message(resolved)
    elif headless:
        verdict["note"] = (
            "the executable Playwright publishes is present, but this server "
            "is configured headless and a headless launch uses a separate "
            "chrome-headless-shell binary whose path Playwright does not "
            "publish. That one is checked by the launch itself."
        )
    return verdict


def assert_ready(playwright: Any, *, headless: bool) -> dict[str, Any]:
    """Return the verdict, or raise with the one actionable line.

    Raises:
        BrowserUnavailableError: no usable browser executable was found. The
            message names the resolved path and the environment variable's
            value, which is what a caller needs in order to act.
    """
    verdict = check(playwright, headless=headless)
    if not verdict["ok"]:
        raise BrowserUnavailableError(verdict["message"])
    return verdict


def translate_launch_failure(exc: Exception, *, headless: bool) -> Exception:
    """Rewrite Playwright's missing-executable error, pass everything else on.

    Returns the SAME exception object untouched unless it is specifically a
    missing-executable failure. That identity is the guarantee: a translator
    that reshaped every error would turn a timeout, a locked profile or a
    crashed browser into a confident lie about a missing binary, which is a
    worse failure than the raw traceback it replaced.

    ``headless`` is accepted so the caller does not have to care which check
    caught the problem; the path comes from Playwright's own message either
    way, so nothing here has to know what a headless binary is called.
    """
    if isinstance(exc, BrowserUnavailableError):
        # Already ours -- assert_ready got there first and said it better.
        return exc
    match = _MISSING_EXECUTABLE.search(str(exc))
    if match is None:
        return exc
    return BrowserUnavailableError(missing_browser_message(match.group(1).strip()))


async def report(*, headless: bool, playwright: Any = None) -> dict[str, Any]:
    """A verdict for a diagnostic tool. Never raises, never launches anything.

    Starts a Playwright driver of its own when one is not supplied -- a local
    node process, measured at roughly 350 ms on this machine, which opens no
    browser and touches no profile -- and stops it again. When the caller
    already has one live, pass it and this costs nothing.
    """
    if playwright is not None:
        return check(playwright, headless=headless)

    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        return {
            "ok": False,
            "resolved_path": None,
            "exists": False,
            "browsers_path_env": browsers_path_setting(),
            "headless": headless,
            "verified_for_this_mode": False,
            "message": (
                f"Playwright is not installed in this server's environment "
                f"({exc}). Fix: pip install playwright && {INSTALL_COMMAND}"
            ),
        }

    started = None
    try:
        started = await async_playwright().start()
        return check(started, headless=headless)
    except Exception as exc:
        return {
            "ok": False,
            "resolved_path": None,
            "exists": False,
            "browsers_path_env": browsers_path_setting(),
            "headless": headless,
            "verified_for_this_mode": False,
            "message": unresolvable_message(f"{type(exc).__name__}: {exc}"),
        }
    finally:
        if started is not None:
            try:
                await started.stop()
            except Exception:  # pragma: no cover - shutdown noise
                pass
