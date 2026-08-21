"""Browser lifecycle: one persistent Chrome profile, one call at a time.

What this module guarantees, and why each guarantee exists:

* **One process on the profile.** ``profile_lock`` is acquired before the
  context launches and released when it closes. Two processes on one Chromium
  user-data dir corrupt it and the operator loses his session.

* **One call at a time.** An ``asyncio.Lock`` serialises tool calls inside
  this process. Nothing here fans out, and nothing runs on a timer.

* **Spacing between navigations.** :data:`config.MIN_NAVIGATION_INTERVAL_S`
  is enforced globally. This is throttling, not disguise -- it is a flat
  minimum interval, deliberately not jittered or randomised to resemble
  anything. Its only job is to stop a burst of tool calls becoming a burst of
  page loads on one human's account.

* **Nothing but reading.** The only Playwright verbs used anywhere in this
  package are ``goto``, waits, and text/JSON reads. There is no click, no
  fill, no form submission, no non-GET request. ``readonly.assert_read_url``
  gates every navigation, and ``tests/test_readonly.py`` greps this package
  to keep it that way.

* **The window does not linger.** After :data:`config.IDLE_CLOSE_S` with no
  tool call the context closes and the lock is released.

The browser is an ordinary Chromium launched by Playwright. It does not spoof
a fingerprint, patch navigator properties, install a stealth plugin, or time
anything to imitate a human. If a plain automated browser cannot see it, this
server does not see it.
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

from linkedin_own_server import profile_lock
from linkedin_own_server.config import (
    CHROME_PROFILE,
    IDLE_CLOSE_S,
    MIN_NAVIGATION_INTERVAL_S,
    NAV_TIMEOUT_MS,
    SETTLE_MS,
    logger,
)
from linkedin_own_server.errors import BrowserUnavailableError
from linkedin_own_server.readonly import assert_read_url

_HEADLESS_ENV = "LINKEDIN_OWN_HEADLESS"


def _headless() -> bool:
    """Headful by default.

    A visible window is the honest option: the operator can watch every page
    this server opens. Headless is available for unattended re-checks of an
    already-live profile, but an interactive sign-in cannot complete in one.
    """
    import os

    return os.environ.get(_HEADLESS_ENV, "").strip().lower() in {"1", "true", "yes"}


class LinkedInBrowser:
    """A single persistent-profile Chromium, started lazily, closed when idle."""

    def __init__(self) -> None:
        self._pw: Any = None
        self._context: Any = None
        self._call_lock = asyncio.Lock()
        self._last_navigation_at: float = 0.0
        self._idle_task: Optional[asyncio.Task] = None
        self._holds_profile_lock = False

    # -- lifecycle ---------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._context is not None

    async def start(self) -> None:
        """Launch the persistent context. Idempotent."""
        if self._context is not None:
            return

        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:  # pragma: no cover - environment
            raise BrowserUnavailableError(
                "Playwright is not installed. Run: pip install playwright && "
                "playwright install chromium"
            ) from exc

        # Refuse to launch if another process owns the profile. Raising here
        # is the point -- corrupting the profile costs the operator his
        # session, which is far worse than a failed tool call.
        profile_lock.acquire()
        self._holds_profile_lock = True

        try:
            CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
            self._pw = await async_playwright().start()
            self._context = await self._pw.chromium.launch_persistent_context(
                user_data_dir=str(CHROME_PROFILE),
                headless=_headless(),
                viewport={"width": 1400, "height": 900},
            )
            self._context.set_default_timeout(NAV_TIMEOUT_MS)
            logger.info(
                "browser started (profile=%s, headless=%s)",
                CHROME_PROFILE,
                _headless(),
            )
        except Exception:
            # Never hold the lock for a browser that did not come up.
            await self._teardown()
            raise

    async def stop(self) -> None:
        """Close the browser and release the profile lock. Never raises."""
        await self._teardown()

    async def _teardown(self) -> None:
        context, pw = self._context, self._pw
        self._context = None
        self._pw = None
        # NB: _idle_close() clears this before calling us, so we never cancel
        # the task we are currently running inside -- doing so would raise
        # CancelledError at the next await and abandon the teardown halfway.
        if self._idle_task is not None:
            self._idle_task.cancel()
            self._idle_task = None
        if context is not None:
            try:
                await context.close()
            except Exception as exc:  # pragma: no cover - shutdown noise
                logger.debug("closing context raised %s: %s", type(exc).__name__, exc)
        if pw is not None:
            try:
                await pw.stop()
            except Exception as exc:  # pragma: no cover - shutdown noise
                logger.debug("stopping playwright raised %s: %s", type(exc).__name__, exc)
        if self._holds_profile_lock:
            profile_lock.release()
            self._holds_profile_lock = False
        logger.info("browser stopped")

    # -- idle close --------------------------------------------------------

    def _touch_idle_timer(self) -> None:
        """(Re)arm the idle close. Best effort -- never fatal to a tool call."""
        if IDLE_CLOSE_S <= 0:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # pragma: no cover - no loop in some tests
            return
        if self._idle_task is not None:
            self._idle_task.cancel()
        self._idle_task = loop.create_task(self._idle_close())

    async def _idle_close(self) -> None:
        try:
            await asyncio.sleep(IDLE_CLOSE_S)
        except asyncio.CancelledError:
            return
        logger.info("idle for %.0fs -- closing the browser", IDLE_CLOSE_S)
        # Clear our own handle first: _teardown cancels self._idle_task, and
        # that task is this one.
        self._idle_task = None
        try:
            await self._teardown()
        except Exception as exc:  # pragma: no cover
            logger.debug("idle close raised %s: %s", type(exc).__name__, exc)

    # -- the one entry point tools use ------------------------------------

    @asynccontextmanager
    async def session(self) -> AsyncIterator[Any]:
        """Yield a page, holding the single-flight lock for the whole call.

        Every tool body runs inside this. Concurrency here would mean two
        navigations racing on one account, which is precisely what the rate
        discipline is meant to prevent.
        """
        async with self._call_lock:
            if self._idle_task is not None:
                self._idle_task.cancel()
                self._idle_task = None
            await self.start()
            page = await self._page()
            try:
                yield page
            finally:
                self._touch_idle_timer()

    async def _page(self) -> Any:
        ctx = self._context
        if ctx is None:  # pragma: no cover - start() just ran
            raise BrowserUnavailableError("browser is not running")
        try:
            pages = [p for p in ctx.pages if not p.is_closed()]
            return pages[0] if pages else await ctx.new_page()
        except Exception as exc:
            raise BrowserUnavailableError(
                f"could not obtain a browser page: {type(exc).__name__}: {exc}"
            ) from exc

    # -- navigation --------------------------------------------------------

    async def wait_for_rate_slot(self) -> float:
        """Sleep until the minimum interval since the last navigation elapses.

        Returns the number of seconds waited, so tools can report it.
        """
        gap = time.monotonic() - self._last_navigation_at
        wait = MIN_NAVIGATION_INTERVAL_S - gap
        if self._last_navigation_at and wait > 0:
            await asyncio.sleep(wait)
            return round(wait, 2)
        return 0.0

    async def goto(self, page: Any, url: str, *, settle_ms: int = SETTLE_MS) -> str:
        """Navigate to an allowlisted read url and let its XHRs settle.

        Returns the FINAL url after any redirect, which is itself a signal:
        LinkedIn bounces signed-out visitors to an auth wall.

        Raises:
            WriteAttemptError: url is not a permitted read surface.
            BrowserUnavailableError: the navigation itself failed.
        """
        assert_read_url(url)
        await self.wait_for_rate_slot()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
        except Exception as exc:
            raise BrowserUnavailableError(
                f"navigation to {url} failed: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            self._last_navigation_at = time.monotonic()

        # One bounded wait for the single-page app to fill the list in. Not a
        # poll loop, and not a scroll -- whatever rendered by now is the result.
        try:
            await page.wait_for_load_state("networkidle", timeout=settle_ms)
        except Exception:
            # networkidle rarely settles on LinkedIn (long-poll connections).
            # Falling through with a flat wait is expected, not an error.
            try:
                await page.wait_for_timeout(settle_ms)
            except Exception as exc:  # pragma: no cover
                logger.debug("settle wait raised %s: %s", type(exc).__name__, exc)

        try:
            return page.url
        except Exception:  # pragma: no cover
            return url


#: Module-level singleton. One server process, one browser, one profile.
BROWSER = LinkedInBrowser()
