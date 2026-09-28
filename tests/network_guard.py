"""No test reaches the network: enforced, not asked.

``tests/conftest.py`` has always opened with "No test in this suite reaches the
network or an account". Until 2026-09-27 the first half was a hope, and it was
false: lane L5 measured eleven tests -- seven in
``tests/test_apply_modal_fixture.py``, four in
``tests/test_verification_that_could_not_read.py`` -- that pressed the apply
anchor of a job posting capture, whose href is LinkedIn's, and sent a fresh
headless Chromium to ``https://www.linkedin.com`` on every run, locally and in
CI. No cookies, no profile, never port 9224; a request to LinkedIn all the
same.

THIS PLUGIN MAKES THE SENTENCE TRUE FOR EVERY BROWSER A TEST OPENS. It is
registered by ``tests/conftest.py`` (``pytest_plugins``), so it runs in CI and
locally with no flag. At configure time it wraps Playwright's three ways to get
a browser context -- ``Browser.new_context``, ``Browser.new_page`` (whose
context is implicit) and ``BrowserType.launch_persistent_context``, async and
sync -- and gives every context one route:

* a request to a loopback host, or to a ``data:``, ``about:``, ``blob:``,
  ``file:`` or browser-internal address, FALLS BACK to whatever the test
  routed itself, and then to the browser;
* every other request is ABORTED before it leaves -- ``blockedbyclient``, so
  the page sees ``net::ERR_BLOCKED_BY_CLIENT``, which a DNS failure never
  produces -- and RECORDED with the test that was running;
* and the test FAILS, LOUDLY, naming itself and every refused address:
  :func:`pytest_runtest_makereport` turns the phase's report red.

A test that serves a page itself -- ``page.route`` fulfilling or aborting --
is untouched, because a page's routes outrank a context's; a request it lets
through with ``route.fallback()`` reaches this guard, as it should.

WHAT IT COVERS, EXACTLY: a request Playwright routes -- one a PAGE makes --
in a browser context THIS process created through one of the three wrapped
calls. Loopback is admitted at every port, by design.

WHAT IT DOES NOT COVER, named rather than implied:

* A CONNECTION MADE OUTSIDE A BROWSER: ``urllib``, ``http.client``,
  ``requests``, a raw socket, Playwright's ``APIRequestContext``. This
  docstring used to add "no test does either today". THAT WAS FALSE, measured
  2026-09-28 by lane S: ``tests/test_tool_envelopes_emit_no_page_string.py``
  drove ``linkedin_cdp_status``, whose probe opened
  ``http://127.0.0.1:<CDP_PORT>/json/version`` with ``urllib`` once per run
  -- loopback, and outside any browser, so this guard saw nothing. The
  harness stubs that probe now, and ``tests/cdp_port_guard.py`` refuses the
  CDP port to every ``socket.connect`` the test process makes.
  A socket census of the full suite, 2026-09-28 (lane G's record, the order of
  04:25, U.7), found no other: 6,022 connection attempts from the test
  processes, every one to loopback outside the CDP ports, none off the
  machine, no name resolved that is not loopback -- and no connection off the
  machine from Node or Chromium, at the sampler's resolution.
* A context this process did not create through the three calls: the
  contexts a browser already holds when a test reaches it with ``connect``
  or ``connect_over_cdp``.
* A browser a test starts in a SUBPROCESS, which this process cannot wrap.
* A browser's own background traffic, which is not a page request: that is
  Playwright's launch flags' business, not a route's.
"""
from __future__ import annotations

import functools
from typing import Any, Callable
from urllib.parse import urlsplit

import pytest

#: Loopback, the only hosts a test may reach.
LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

#: Addresses that name no host at all: inline documents and the browser's own
#: pages. ``chrome-error`` is where a refused navigation lands.
LOCAL_SCHEMES = frozenset(
    {"about", "blob", "data", "file", "chrome", "chrome-error", "chrome-extension", "devtools"}
)

#: What a page sees for a refused request. Chosen because nothing else
#: produces it: a request that failed at DNS reads ERR_NAME_NOT_RESOLVED.
ABORT_CODE = "blockedbyclient"


def is_local(url: str) -> bool:
    """Does ``url`` stay on this machine?"""
    parts = urlsplit(str(url or ""))
    if parts.scheme.lower() in LOCAL_SCHEMES:
        return True
    return (parts.hostname or "").lower() in LOCAL_HOSTS


#: Every refusal since the last report was made: ``(test node id, url)``. One
#: list per process, which under xdist is one per worker.
_REFUSED: list[tuple[str, str]] = []

#: The test running now, so a refusal is attributed to the test that caused it
#: even when it is reported in a later phase.
_RUNNING: dict[str, str] = {"nodeid": "<no test running>"}


def take_refused() -> list[tuple[str, str]]:
    """The refusals recorded since the last report, and forget them.

    A test that plants a request ON PURPOSE -- this file's own controls --
    takes its refusal here, so the report does not fail it for the request it
    set out to make."""
    taken = list(_REFUSED)
    _REFUSED.clear()
    return taken


def _refuse(url: str) -> bool:
    """Record ``url`` if it leaves the machine. True when it must be aborted."""
    if is_local(url):
        return False
    _REFUSED.append((_RUNNING["nodeid"], url))
    return True


async def _route(route: Any) -> None:
    if _refuse(route.request.url):
        await route.abort(ABORT_CODE)
    else:
        await route.fallback()


def _route_sync(route: Any) -> None:
    if _refuse(route.request.url):
        route.abort(ABORT_CODE)
    else:
        route.fallback()


#: ``(owner, attribute, original)`` for every wrap, so unconfigure restores it.
_WRAPPED: list[tuple[Any, str, Any]] = []


def _wrap(owner: Any, name: str, make: Callable[[Any], Any]) -> None:
    original = getattr(owner, name)
    replacement = functools.wraps(original)(make(original))
    setattr(owner, name, replacement)
    _WRAPPED.append((owner, name, original))


def _wrap_async(api: Any) -> None:
    def contexts(original: Any) -> Any:
        async def guarded(self: Any, *args: Any, **kwargs: Any) -> Any:
            context = await original(self, *args, **kwargs)
            await context.route("**/*", _route)
            return context

        return guarded

    def pages(original: Any) -> Any:
        async def guarded(self: Any, *args: Any, **kwargs: Any) -> Any:
            page = await original(self, *args, **kwargs)
            await page.context.route("**/*", _route)
            return page

        return guarded

    _wrap(api.Browser, "new_context", contexts)
    _wrap(api.Browser, "new_page", pages)
    _wrap(api.BrowserType, "launch_persistent_context", contexts)


def _wrap_sync(api: Any) -> None:
    def contexts(original: Any) -> Any:
        def guarded(self: Any, *args: Any, **kwargs: Any) -> Any:
            context = original(self, *args, **kwargs)
            context.route("**/*", _route_sync)
            return context

        return guarded

    def pages(original: Any) -> Any:
        def guarded(self: Any, *args: Any, **kwargs: Any) -> Any:
            page = original(self, *args, **kwargs)
            page.context.route("**/*", _route_sync)
            return page

        return guarded

    _wrap(api.Browser, "new_context", contexts)
    _wrap(api.Browser, "new_page", pages)
    _wrap(api.BrowserType, "launch_persistent_context", contexts)


def pytest_configure(config: Any) -> None:
    try:
        from playwright import async_api, sync_api
    except ImportError:  # pragma: no cover - no browser, nothing to guard
        return
    _wrap_async(async_api)
    _wrap_sync(sync_api)


def pytest_unconfigure(config: Any) -> None:
    while _WRAPPED:
        owner, name, original = _WRAPPED.pop()
        setattr(owner, name, original)


def pytest_runtest_logstart(nodeid: str, location: Any) -> None:
    _RUNNING["nodeid"] = nodeid


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Any:
    outcome = yield
    report = outcome.get_result()
    refused = take_refused()
    if not refused:
        return
    lines = "\n".join(f"    {url}  (refused while {nodeid} ran)" for nodeid, url in refused)
    message = (
        f"{item.nodeid} REACHED FOR THE NETWORK during {report.when}: "
        f"{len(refused)} request(s) to an address off this machine, each refused "
        f"before it left (tests/network_guard.py):\n{lines}\n"
        "A test serves every page it needs locally -- a frozen capture through "
        "page.route or set_content -- and never lets the browser fetch one."
    )
    if report.failed:
        report.sections.append(("network guard", message))
    else:
        report.outcome = "failed"
        report.longrepr = message
