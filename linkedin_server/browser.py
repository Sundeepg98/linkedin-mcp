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

The browser is an ordinary Chromium launched by Playwright with the two flags
enumerated in :data:`config.LAUNCH_ARGS` and nothing else. It does not install
a stealth plugin, spoof a user agent, platform, canvas, font list or timezone,
route through a proxy, or time anything to imitate a human. What one of those
two flags does do is stop Blink setting ``navigator.webdriver = true``, which
is the difference between LinkedIn completing a sign-in and refusing one; that
is a single Blink feature switch, it is what the sibling Naukri server has run
for months, and the boundary stops there. ``tests/test_launch_boundary.py``
holds the line as an executable check rather than a promise.

TWO MODES, and the second is for recovery only:

* **LAUNCH (default).** Playwright starts Chromium against the persistent
  profile at :data:`config.CHROME_PROFILE`. The session lives in that profile
  and survives restarts and reboots. This is the daily path. Before it takes
  the profile lock, ``preflight`` asks Playwright whether a browser
  executable is actually there, so a missing install fails with one
  actionable line naming the resolved path and ``PLAYWRIGHT_BROWSERS_PATH``
  rather than a raw traceback that has already been misdiagnosed once.
* **ATTACH.** With ``LINKEDIN_CDP_ATTACH=1`` this server launches nothing
  and connects over CDP to a Chrome the operator started himself. It takes no
  profile lock (it owns no profile), it opens its own tab rather than driving
  one of his, and on teardown it disconnects without closing his browser --
  measured, not assumed. See ``cdp_bridge.py`` for the exact requirements.
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

from linkedin_server import preflight, profile_lock
from linkedin_server.session_store import SessionStore
from linkedin_server.config import (
    CDP_ATTACH,
    CHROME_PROFILE,
    IDLE_CLOSE_S,
    LAUNCH_ARGS,
    MIN_NAVIGATION_INTERVAL_S,
    NAV_TIMEOUT_MS,
    SETTLE_MS,
    logger,
)
from linkedin_server.errors import BrowserUnavailableError
from linkedin_server.readonly import (
    assert_launch_flags_permitted,
    assert_read_url,
)

_HEADLESS_ENV = "LINKEDIN_HEADLESS"


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
        #: Evidence about how the most recent navigation SETTLED. Written by
        #: goto, read by diagnostics, never by control flow here. See the
        #: ``last_settle`` property for why a caller wants it.
        self._last_settle: dict[str, Any] = {}
        self._idle_task: Optional[asyncio.Task] = None
        self._holds_profile_lock = False
        #: Set only in ATTACH mode: the CDP client we must disconnect, and the
        #: tab we opened. Both stay None on the ordinary launch path.
        self._cdp_client: Any = None
        self._own_page: Any = None

    # -- lifecycle ---------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._context is not None

    @property
    def attached(self) -> bool:
        """True when this server is driving a browser it did not start."""
        return self._cdp_client is not None

    @property
    def mode(self) -> str:
        """``"attach"`` or ``"launch"`` -- what the NEXT start() would do."""
        return "attach" if CDP_ATTACH else "launch"

    @property
    def headless(self) -> bool:
        """Whether the NEXT launch would be headless."""
        return _headless()

    @property
    def last_settle(self) -> dict[str, Any]:
        """How the MOST RECENT navigation settled. Empty before the first one.

        WHY A CALLER WANTS THIS. ``goto``'s settle has exactly two outcomes and
        they are seven seconds apart -- see the comment in ``goto`` -- so a
        reader that found nothing on the page has no way, from the page alone,
        to tell "LinkedIn did not send it" from "I looked one second after
        DOMContentLoaded and it had not arrived yet". Those want opposite
        responses: the first is a finding, the second is a re-read. This is the
        field that separates them, and it costs nothing -- it is measured
        during a wait that was happening anyway.

        Three keys: ``branch`` (``networkidle_resolved``,
        ``networkidle_timed_out`` or ``settle_failed``), ``settled_ms`` (what
        the settle actually cost) and ``settle_ms_configured``. A copy, so a
        caller cannot edit the record.

        NOT a readiness check and never to be used as one. It reports how long
        this navigation waited, not whether what you wanted had drawn. A
        reader that needs a specific element must wait for that element.
        """
        return dict(self._last_settle)

    @property
    def playwright(self) -> Any:
        """The live Playwright driver, or ``None``.

        Exposed so a diagnostic can run the browser preflight against the
        driver that is ALREADY up instead of starting a second one. Read
        only: nothing outside this class drives it.
        """
        return self._pw

    async def start(self) -> None:
        """Bring up a browser context. Idempotent.

        In the default LAUNCH mode this starts Chromium against the persistent
        profile, holding the cross-process profile lock for as long as it
        lives. In ATTACH mode it connects to a browser the operator already
        started and takes NO profile lock -- it does not own that profile, and
        claiming a lock on a directory another Chrome is actively using would
        be a lie that blocks the launch path for no benefit.
        """
        if self._context is not None:
            return

        if CDP_ATTACH:
            await self._start_attached()
            return

        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:  # pragma: no cover - environment
            raise BrowserUnavailableError(
                "Playwright is not installed. Run: pip install playwright && "
                "playwright install chromium"
            ) from exc

        # The driver first, and deliberately before the profile lock. Starting
        # it opens a local node process; it launches no browser, reads no
        # profile and touches no network, and it is what lets the preflight
        # below ask Playwright itself where the browser is.
        self._pw = await async_playwright().start()

        headless = _headless()
        try:
            # Three gates, in this order, and the order is the design.
            #
            # FIRST the launch boundary, enforced at runtime and not only in
            # the test suite: a flag added here never reaches Chromium unless
            # it is one the operator sanctioned. It goes first because it is
            # the only one of the three that is a SECURITY invariant, it
            # depends on nothing outside this process, and it must therefore
            # hold identically on a machine with no browser installed at all.
            assert_launch_flags_permitted(LAUNCH_ARGS)
            # THEN, is there a browser to launch? Before the lock on purpose:
            # a missing executable that had already taken the profile lock
            # would be reported to the operator as a locked profile, sending
            # him after the wrong problem. See preflight.py for the day this
            # cost a wrong diagnosis and nearly 150 MB onto a full drive.
            preflight.assert_ready(self._pw, headless=headless)
            # LAST, refuse to launch if another process owns the profile.
            # Raising here is the point -- corrupting the profile costs the
            # operator his session, which is far worse than a failed tool
            # call -- and it is last because it is the only gate of the three
            # that changes anything on disk.
            profile_lock.acquire()
            self._holds_profile_lock = True
            CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
            self._context = await self._pw.chromium.launch_persistent_context(
                user_data_dir=str(CHROME_PROFILE),
                headless=headless,
                viewport={"width": 1400, "height": 900},
                args=list(LAUNCH_ARGS),
            )
            self._context.set_default_timeout(NAV_TIMEOUT_MS)
            logger.info(
                "browser started (profile=%s, headless=%s, args=%s)",
                CHROME_PROFILE,
                headless,
                list(LAUNCH_ARGS),
            )
            # PUT THE SESSION BACK IF CHROME THREW IT AWAY.
            #
            # This profile carries a NEWER Chrome's version stamp than
            # playwright's chromium -- his own Chrome 151 opened it once --
            # so Chrome runs its downgrade migration on launch, moves the
            # profile aside and starts clean. Measured 2026-08-25: that is
            # what made him sign in over and over while naukri, whose profile
            # carries playwright's own stamp, held a session for days.
            #
            # ADDITIVE AND CONDITIONAL. The profile is untouched and remains
            # the primary source; this injects the stored jar ONLY into a
            # context that has no session cookie, so a working profile is
            # never overwritten with an older one. Every failure path returns
            # "restored: False" and leaves the launch exactly as it was.
            try:
                outcome = await SESSION_STORE.restore_into_context(self._context)
                if outcome.get("restored"):
                    logger.info("session store: %s", outcome.get("why"))
            except Exception as exc:  # noqa: BLE001 - a net, never a gate
                logger.debug(
                    "session restore skipped (%s): %s", type(exc).__name__, exc
                )
        except Exception as exc:
            # Never hold the lock, or a driver, for a browser that did not
            # come up.
            await self._teardown()
            # The preflight cannot cover a headless launch (Playwright does
            # not publish that binary's path), so the launch's OWN failure is
            # translated with the path Playwright named. Anything that is not
            # a missing executable comes back unchanged -- a translator that
            # reshaped every error would turn a timeout into a confident lie.
            translated = preflight.translate_launch_failure(exc, headless=headless)
            if translated is exc:
                raise
            raise translated from exc

    async def _start_attached(self) -> None:
        """Connect to a browser the operator started. Recovery path only."""
        from linkedin_server import cdp_bridge

        pw, client, context = await cdp_bridge.attach()
        self._pw = pw
        self._cdp_client = client
        self._context = context
        try:
            self._context.set_default_timeout(NAV_TIMEOUT_MS)
        except Exception as exc:  # pragma: no cover - older client
            logger.debug("set_default_timeout raised %s: %s", type(exc).__name__, exc)
        logger.info("attached over CDP at %s", cdp_bridge.endpoint())

    async def stop(self) -> None:
        """Close the browser and release the profile lock. Never raises."""
        await self._teardown()

    async def _teardown(self) -> None:
        context, pw = self._context, self._pw
        client, own_page = self._cdp_client, self._own_page
        self._context = None
        self._pw = None
        self._cdp_client = None
        self._own_page = None
        # NB: _idle_close() clears this before calling us, so we never cancel
        # the task we are currently running inside -- doing so would raise
        # CancelledError at the next await and abandon the teardown halfway.
        if self._idle_task is not None:
            self._idle_task.cancel()
            self._idle_task = None

        if client is not None:
            # ATTACH mode. The context belongs to the operator's browser, so
            # closing it would close HIS window. Close only the tab we opened,
            # then drop the CDP connection: measured on this machine, the
            # client's close() disconnects and leaves Chrome serving.
            if own_page is not None:
                try:
                    await own_page.close()
                except Exception as exc:  # pragma: no cover - shutdown noise
                    logger.debug("closing our tab raised %s: %s", type(exc).__name__, exc)
            try:
                await client.close()
            except Exception as exc:  # pragma: no cover - shutdown noise
                logger.debug("cdp disconnect raised %s: %s", type(exc).__name__, exc)
        elif context is not None:
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

        if self._cdp_client is not None:
            # ATTACH mode: every existing tab is one the operator opened, and
            # navigating one away would yank a page out from under him. We
            # always work in a tab of our own. (A probe of this box also found
            # extensions opening and driving their own tabs in a freshly made
            # profile, so "tab zero is mine" is not merely rude, it is wrong.)
            try:
                page = self._own_page
                if page is not None and not page.is_closed():
                    return page
                self._own_page = await ctx.new_page()
                return self._own_page
            except Exception as exc:
                raise BrowserUnavailableError(
                    f"could not open a tab in the attached browser: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc

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
        #
        # IT HAS TWO OUTCOMES AND THEY ARE SEVEN SECONDS APART. If networkidle
        # resolves, the read that follows is taken ~0 ms from here. If it times
        # out, the flat wait runs as well and the read is taken 2 x settle_ms
        # from here. Which one happens is decided by whether the page found a
        # 500 ms lull, so it is a race, and it is why ``last_settle`` exists.
        #
        # THE COMMENT THAT USED TO SIT HERE SAID "networkidle rarely settles on
        # LinkedIn (long-poll connections)". Measured 2026-08-30 against the MCP
        # client's own call log, that is true of ONE surface and false of
        # another: /jobs/search resolved early in 0 of 10 recorded loads and has
        # never failed, while /jobs/view/<id> resolved early in 28 of 37. Across
        # the 15 reads whose outcome was recorded, the split is total -- 13 of 13
        # early reads refused for a missing description, 2 of 2 timed-out reads
        # drew the posting in full, over four different postings. One of them
        # drew 22 s after the same url had been refused; another drew after
        # failing about twelve times, every one of those on the early branch.
        # Believing the old comment is what kept this hidden for a day.
        # _audit/2026-08-30-jobs-view-reliability.md carries the probe log.
        settle_started = time.monotonic()
        branch = "networkidle_resolved"
        try:
            await page.wait_for_load_state("networkidle", timeout=settle_ms)
        except Exception:
            # Falling through with a flat wait is expected, not an error.
            branch = "networkidle_timed_out"
            try:
                await page.wait_for_timeout(settle_ms)
            except Exception as exc:  # pragma: no cover
                branch = "settle_failed"
                logger.debug("settle wait raised %s: %s", type(exc).__name__, exc)
        self._last_settle = {
            "branch": branch,
            "settled_ms": round((time.monotonic() - settle_started) * 1000),
            "settle_ms_configured": settle_ms,
        }

        try:
            return page.url
        except Exception:  # pragma: no cover
            return url


#: Module-level singleton. One server process, one browser, one profile.
#: The server's OWN copy of the session, beside the profile rather than in it.
#: See session_store.py: the profile is still the primary source and is never
#: written to or deleted by this: the store is a net for the case Chrome
#: discards the profile on launch, which this profile provokes because it
#: carries a newer Chrome's version stamp than playwright's chromium.
SESSION_STORE = SessionStore()

BROWSER = LinkedInBrowser()
