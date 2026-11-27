"""The notifications reader reads LinkedIn's server-driven page, and the old one still reads 9 of 9.

Lane msg7, 2026-11-27, ``_audit/2026-11-27-msg7.md`` section 7. On live
session 12's capture of ``/notifications/`` (load 38,
``tests/fixtures/live12/notifications.html``) the shipped
``dom.NOTIFICATION_SELECTORS`` harvest read 0 records: the page is one
server-driven screen with no ``article`` card. CAPTURE-SHOWS-READER-BLIND-DEMOTES
(the orchestrator, 2026-11-27) made the server-driven read this lane's, red
first, with session 5's page (``tests/fixtures/live5/notifications.html``, the
old design, 9 cards) kept as a CONTROL that must stay green.

Every page here is a tracked fixture or a few lines of markup written below,
loaded into a LOCAL headless engine with EVERY request aborted. Nothing reaches
LinkedIn. The fixtures' texts are reduced to ``x``; nothing asserts a word of
any person's.
"""
from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

import pytest

from linkedin_server import dom, notification_cards, server, shape

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SDUI_PAGE = FIXTURES / "live12" / "notifications.html"
CLASSIC_PAGE = FIXTURES / "live5" / "notifications.html"
NOTIFICATIONS_URL = "https://www.linkedin.com/notifications/"

#: A screen drawing one link that names a label OUTSIDE itself: not a card.
OUTSIDE_LABEL = """<!doctype html><html><body><main>
<div data-sdui-screen="x">
  <div id="sentence-1">Somebody did something</div>
  <div><a href="https://www.linkedin.com/feed/" aria-labelledby="sentence-1">open</a>
  <p>2h</p><button aria-label="More options" aria-expanded="false"></button></div>
</div></main></body></html>"""


class _Navigator:
    def __init__(self, html: str):
        self.html = html
        self.gotos: list[str] = []

    async def goto(self, page, url, **_ignored):
        self.gotos.append(url)
        await page.set_content(self.html, wait_until="domcontentloaded", timeout=60_000)
        return NOTIFICATIONS_URL


class _Browser:
    def __init__(self, page, navigator):
        self.page = page
        self.navigator = navigator

    @contextlib.asynccontextmanager
    async def session(self):
        yield self.page

    async def goto(self, page, url, **kwargs):
        return await self.navigator.goto(page, url, **kwargs)


async def _read(html: str) -> dict:
    playwright = pytest.importorskip("playwright.async_api")
    out: dict = {}
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.route("**/*", lambda route: asyncio.ensure_future(route.abort()))
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            records, design = await notification_cards.harvest(page, max_items=40)
            out["records"], out["design"] = records, design
            out["expanded_after"] = await page.locator('[aria-expanded="true"]').count()
            navigator = _Navigator(html)
            original = server.BROWSER
            server.BROWSER = _Browser(page, navigator)
            try:
                out["tool"] = await server.linkedin_notifications(limit=20)
            finally:
                server.BROWSER = original
            out["gotos"] = list(navigator.gotos)
        finally:
            await browser.close()
    return out


@pytest.fixture(scope="module")
def sdui() -> dict:
    return asyncio.run(_read(SDUI_PAGE.read_text(encoding="utf-8")))


@pytest.fixture(scope="module")
def classic() -> dict:
    return asyncio.run(_read(CLASSIC_PAGE.read_text(encoding="utf-8")))


def _kind(href: str) -> str:
    for kind in ("/jobs/", "/analytics/", "/in/", "/feed/"):
        if kind in href:
            return kind
    return "other"


def test_the_server_driven_page_reads_its_ten_cards(sdui):
    assert sdui["design"] == notification_cards.SDUI
    records = sdui["records"]
    assert len(records) == 10, len(records)
    kinds = {}
    for record in records:
        assert record["text"], record
        assert record["href"].startswith("https://www.linkedin.com/"), record["href"][:40]
        assert record["selector"] == notification_cards.SELECTOR_NAME
        kinds[_kind(record["href"])] = kinds.get(_kind(record["href"]), 0) + 1
    # The paths session 12's keyed skeleton measured: 7 job searches, one
    # analytics page, one member, one feed address.
    assert kinds == {"/jobs/": 7, "/analytics/": 1, "/in/": 1, "/feed/": 1}, kinds


def test_each_card_carries_its_time_from_beside_its_menu_trigger(sdui):
    assert all(record["time"] for record in sdui["records"]), [r["time"] for r in sdui["records"]]


def test_unread_is_not_reported_as_read_on_the_server_driven_design(sdui):
    # No unread marking on this design has been measured: None, never False.
    assert all(record["unread"] is None for record in sdui["records"])
    tool = sdui["tool"]
    assert tool.get("unread_when_read") is None, tool.get("unread_when_read")
    assert all("unread" not in row for row in tool["results"]), tool["results"][:1]


def test_the_tool_returns_ten_rows_on_the_server_driven_page(sdui):
    tool = sdui["tool"]
    assert "error" not in tool, str(tool)[:300]
    assert len(tool["results"]) == 10, len(tool["results"])
    assert tool.get("page_design") == notification_cards.SDUI
    assert sdui["gotos"] == [NOTIFICATIONS_URL]
    for row in tool["results"]:
        assert row["text"]
        assert row["link"].startswith("https://www.linkedin.com/")
        assert "?" not in row["link"], "the published link keeps no query"


def test_the_seven_job_alert_rows_publish_one_link(sdui):
    """M C97's key, in the form a caller can name. ``shape.absolute_url``
    deletes the query, so the seven job-alert cards -- distinct only by query
    on session 12's keyed skeleton (record s7.1) -- publish ONE link, and a
    delete keyed by the published link would refuse all seven."""
    links = [row["link"] for row in sdui["tool"]["results"]]
    jobs = {link for link in links if "/jobs/" in link}
    assert len([link for link in links if "/jobs/" in link]) == 7
    assert len(jobs) == 1, jobs


def test_nothing_is_pressed_and_nothing_navigates_while_reading(sdui):
    assert sdui["expanded_after"] == 0


def test_control_the_classic_page_still_reads_nine_of_nine(classic):
    assert classic["design"] == notification_cards.CLASSIC
    assert len(classic["records"]) == 9, len(classic["records"])
    tool = classic["tool"]
    assert "error" not in tool, str(tool)[:300]
    assert len(tool["results"]) == 9
    assert tool.get("page_design") == notification_cards.CLASSIC


def test_a_link_labelled_from_outside_itself_is_not_a_card():
    out = asyncio.run(_read(OUTSIDE_LABEL))
    # The screen is drawn but holds no card, so the old harvest runs -- and
    # the page's one paragraph is no notification card either.
    assert [r for r in out["records"] if r["selector"] == notification_cards.SELECTOR_NAME] == []
    assert out["design"] == notification_cards.CLASSIC


def test_the_old_selectors_alone_read_nothing_on_the_server_driven_page():
    """THE REGRESSION, held: what the shipped harvest alone reads on session
    12's page. If this ever reads cards, the old selectors have changed and the
    server-driven read's premise should be looked at again."""

    async def run() -> int:
        playwright = pytest.importorskip("playwright.async_api")
        async with playwright.async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.route("**/*", lambda route: asyncio.ensure_future(route.abort()))
                await page.set_content(SDUI_PAGE.read_text(encoding="utf-8"),
                                       wait_until="domcontentloaded", timeout=60_000)
                records = await dom.harvest_block_cards(
                    page, selectors=dom.NOTIFICATION_SELECTORS, max_items=40,
                    hidden_selector=dom.NOTIFICATION_HIDDEN_SELECTOR,
                    time_selector=dom.NOTIFICATION_TIME_SELECTOR,
                    unread_class=dom.NOTIFICATION_UNREAD_CLASS)
                return len(records)
            finally:
                await browser.close()

    assert asyncio.run(run()) == 0


def test_the_shipped_shaper_takes_every_server_driven_record(sdui):
    rows, dropped = dom.parse_all(sdui["records"], shape.parse_notification)
    assert len(rows) == 10
    assert not dropped, dropped
