"""Fakes for a browser that is never launched.

No test in this suite reaches the network or an account. Nearly all of them
run with no Chromium either, on the fakes below: they stand in for the three
Playwright objects this server touches -- a page, its browser context, and
its request context -- and they RECORD what was asked of them, so a test can
assert not just the answer but that the question was actually put to
LinkedIn.

The exception is ``test_profile_views_fixture.py``, which launches a LOCAL
headless Chromium over frozen markup and still touches nothing outside this
machine. It has to: the bug it pins lives in a DOM walk, and a fake page
cannot walk a DOM. That module says more about why.

That recording is the point. The failure this suite exists to prevent is a
server that reports a live session without ever asking whether there is one,
and the only way to catch that is to count the requests.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import pytest


class FakeResponse:
    """A Playwright APIResponse stand-in."""

    def __init__(self, status: int, body: Any = ""):
        self.status = status
        self._body = body if isinstance(body, str) else json.dumps(body)

    async def text(self) -> str:
        return self._body


class FakeRequestContext:
    """``page.request`` -- hands back queued responses and logs every call."""

    def __init__(self, responses: Optional[list] = None, default: Any = None):
        self._queue = list(responses or [])
        #: Returned once the queue empties. Lets a test model "LinkedIn keeps
        #: saying no" without guessing how many times the server will ask.
        self.default = default
        self.calls: list[dict[str, Any]] = []

    async def get(self, url: str, headers=None, timeout=None):
        self.calls.append({"url": url, "headers": dict(headers or {})})
        if not self._queue and self.default is not None:
            return self.default
        if not self._queue:
            raise AssertionError(
                f"unexpected request to {url}: the fake has no response left. "
                "A test that runs out of queued responses is usually a server "
                "asking more often than the test expected."
            )
        item = self._queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def queue(self, *responses) -> None:
        self._queue.extend(responses)


class FakeBrowserContext:
    """``page.context`` -- owns the cookie jar."""

    def __init__(
        self,
        cookies: Optional[dict[str, str]] = None,
        expiries: Optional[dict[str, float]] = None,
    ):
        self.jar = dict(cookies or {})
        #: name -> expiry, seconds since the epoch. Playwright reports -1 for
        #: a cookie that dies with the browser, and that is the default here
        #: because it is what LinkedIn's JSESSIONID actually is.
        self.expiries = dict(expiries or {})
        self.cookie_reads = 0

    async def cookies(self, url: Optional[str] = None) -> list[dict[str, Any]]:
        self.cookie_reads += 1
        return [
            {"name": k, "value": v, "expires": self.expiries.get(k, -1)}
            for k, v in self.jar.items()
        ]


class FakePage:
    """A page that can be navigated, read and closed, and remembers all three."""

    def __init__(
        self,
        *,
        cookies: Optional[dict[str, str]] = None,
        responses: Optional[list] = None,
        url: str = "https://www.linkedin.com/feed/",
        evaluate_result: Any = None,
        default_response: Any = None,
        expiries: Optional[dict[str, float]] = None,
        cookies_after_goto: Optional[dict[str, str]] = None,
    ):
        self.context = FakeBrowserContext(cookies, expiries)
        #: Cookies LinkedIn issues once a page is actually loaded. This is how
        #: a cold browser behaves: the persistent li_at is already in the jar,
        #: and the session cookie the identity call needs only appears after
        #: something has been fetched.
        self.cookies_after_goto = dict(cookies_after_goto or {})
        self.request = FakeRequestContext(responses, default=default_response)
        self.url = url
        self.gotos: list[str] = []
        self.evaluations: list[tuple[str, Any]] = []
        self.evaluate_result = evaluate_result
        self._closed = False
        #: url the next goto should land on, if it differs from the target
        #: (a redirect to the auth wall, for instance).
        self.redirect_to: Optional[str] = None

    async def goto(self, url: str, **kwargs) -> None:
        self.gotos.append(url)
        self.url = self.redirect_to or url
        if self.cookies_after_goto:
            self.context.jar.update(self.cookies_after_goto)
            self.cookies_after_goto = {}

    async def wait_for_load_state(self, *args, **kwargs) -> None:
        return None

    async def wait_for_timeout(self, *args, **kwargs) -> None:
        return None

    async def evaluate(self, script: str, arg: Any = None) -> Any:
        self.evaluations.append((script, arg))
        result = self.evaluate_result
        if isinstance(result, Exception):
            raise result
        return result

    def is_closed(self) -> bool:
        return self._closed

    def close_window(self) -> None:
        """Simulate the operator closing the login window."""
        self._closed = True

    async def close(self) -> None:
        """Playwright's own page.close(). Used by the attach-mode teardown."""
        self._closed = True


def me_response(
    first: str = "Sundeep",
    last: str = "G",
    public_id: str = "sundeep-g",
) -> FakeResponse:
    """A 200 from /voyager/api/me shaped the way LinkedIn shapes it."""
    return FakeResponse(
        200,
        {
            "data": {
                "plainId": 123456,
                "miniProfile": {
                    "firstName": first,
                    "lastName": last,
                    "publicIdentifier": public_id,
                },
            },
            "included": [],
        },
    )


@pytest.fixture
def signed_in_page() -> FakePage:
    """A page whose identity endpoint answers with a member."""
    return FakePage(cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
                    responses=[me_response()])


@pytest.fixture
def signed_out_page() -> FakePage:
    """A page holding a cookie that LinkedIn refuses.

    This is the shape of the bug this server was built to avoid: the cookie is
    right there, and the answer is still no.
    """
    return FakePage(cookies={"li_at": "stale", "JSESSIONID": '"ajax:1"'},
                    responses=[FakeResponse(401, "")])


@pytest.fixture
def patched_navigation(monkeypatch):
    """Replace BROWSER.goto with a recorder, so nothing launches Chromium."""
    from linkedin_own_server import browser as browser_module

    navigations: list[str] = []

    async def fake_goto(page, url, **kwargs):
        navigations.append(url)
        await page.goto(url)
        return page.url

    monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
    return navigations
