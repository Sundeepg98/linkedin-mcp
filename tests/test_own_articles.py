"""Pins for ``linkedin_server.own_articles`` -- census row ``M C48``, "View all
your articles" -- over the TRACKED skeleton of the page the live lane's
session 1 captured, ``tests/fixtures/live1/articles.html`` (built by
``scripts/_build_live1_l1_fixtures.py``; every value in it is ``x``).

WHAT THE SKELETON DRAWS, measured (lane B3, 2026-10-10): one section in
``main`` whose heading is LinkedIn's "All activity", a filter nav with one
pill, and ONE SDUI screen slot (``data-sdui-screen``) holding a single
childless container. No ``/pulse/`` link, no list, no empty-state words.

THE POSITIVE PATH HAS NO CAPTURE. He has published no article that any
capture shows, so the one-article reading is taken on a COPY of the real
skeleton with ONE synthetic ``/pulse/`` anchor planted inside that slot's
container, where the measured page would draw an entry. That entry's shape is
DERIVED, and the module docstring says so.

Every page here is loaded into a throwaway headless chromium by
``set_content``; the network guard aborts anything that would leave the box.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from linkedin_server import own_articles

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "live1" / "articles.html"

#: Synthetic, declared here: no real article, no real person's slug.
SYNTHETIC_SLUG = "example-synthetic-article"
SYNTHETIC_TITLE = "Example synthetic article"

#: The childless container inside the page's screen slot, as the tracked copy
#: writes it: the slot's opening tag, then the container's, then its close.
_SLOT_CONTAINER = re.compile(
    r'(<div class="[^"]*" data-sdui-screen="x">\n<div class="[^"]*">\n)(</div>)'
)


def _with_planted_article(html: str, anchor: str) -> str:
    """The real skeleton with ``anchor`` planted in the screen slot's
    container. Refuses if the skeleton stopped drawing that container."""
    planted, count = _SLOT_CONTAINER.subn(lambda m: m.group(1) + anchor + "\n" + m.group(2), html)
    assert count == 1, "the skeleton no longer draws exactly one childless screen slot container"
    return planted


async def _refused(route) -> None:
    await route.abort()


async def _read(html: str):
    """Load ``html`` into a throwaway headless page and read it. The skeleton
    keeps its iframes' and images' shaped addresses, which a browser would
    try to fetch: the page's own route refuses every request first."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            await page.route("**/*", _refused)
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await own_articles.read_own_articles(page)
        finally:
            await browser.close()


async def test_the_real_skeleton_reads_as_his_articles_screen_drawn_empty():
    """The measured page: readable, no article, and EMPTY because the page's
    own screen slot drew its container with nothing in it -- not because the
    article count is zero."""
    reading = await _read(FIXTURE.read_text(encoding="utf-8"))
    assert reading["readable"] is True
    assert reading["articles"] == []
    assert reading["count"] == 0
    assert reading["empty"] is True
    assert reading["truncated"] is False
    assert reading["links_seen"] == 0


async def test_one_planted_article_on_a_copy_of_the_real_skeleton_is_read():
    """The DERIVED positive path: one synthetic entry where the page would
    draw it. Its title comes back sanitised; its link as a ``/pulse/`` path,
    the query and the host dropped."""
    zero_width = chr(0x200B)
    anchor = (
        '<a href="https://www.linkedin.com/pulse/' + SYNTHETIC_SLUG + '/?trackingId=x">'
        + "  Example " + zero_width + "synthetic   article </a>"
    )
    reading = await _read(_with_planted_article(FIXTURE.read_text(encoding="utf-8"), anchor))
    assert reading["readable"] is True
    assert reading["empty"] is False
    assert reading["count"] == 1
    assert reading["articles"] == [
        {"title": SYNTHETIC_TITLE, "link": "/pulse/" + SYNTHETIC_SLUG + "/"}
    ]


async def test_a_link_that_is_not_his_article_is_counted_never_returned():
    """Another host's ``/pulse/``, a ``/pulse/`` path with more segments, and a
    post permalink: each is a link the slot drew, none is an article."""
    anchors = "\n".join([
        '<a href="https://example.com/pulse/' + SYNTHETIC_SLUG + '/">x</a>',
        '<a href="/pulse/' + SYNTHETIC_SLUG + '/extra/">x</a>',
        '<a href="/feed/update/urn:li:activity:1/">x</a>',
    ])
    reading = await _read(_with_planted_article(FIXTURE.read_text(encoding="utf-8"), anchors))
    assert reading["readable"] is True
    assert reading["articles"] == []
    assert reading["count"] == 0
    assert reading["links_seen"] == 3
    assert reading["not_article_links"] == 3
    # Links were drawn, so the slot is not empty -- and zero articles is
    # still not "empty": the two are different facts.
    assert reading["empty"] is False


async def test_a_page_without_the_activity_heading_is_not_readable():
    """No "All activity" section: nothing here is his articles list, so the
    reading is unreadable and never empty."""
    html = FIXTURE.read_text(encoding="utf-8").replace("All activity", "x")
    reading = await _read(html)
    assert reading["readable"] is False
    assert reading["empty"] is False
    assert reading["articles"] == []


def test_link_of_keeps_only_a_pulse_path_on_linkedin():
    assert own_articles.link_of("https://www.linkedin.com/pulse/a-b-c/") == "/pulse/a-b-c/"
    assert own_articles.link_of("/pulse/a-b-c") == "/pulse/a-b-c/"
    assert own_articles.link_of("/pulse/a-b-c/?trk=x#y") == "/pulse/a-b-c/"
    for refused in (
        None, "", "https://example.com/pulse/a/", "http://www.linkedin.com/pulse/a/",
        "/pulse/", "/pulse/a/b/", "/pulse/a b/", "/in/someone/", "javascript:alert(1)",
        "/pulse/" + "a" * 201 + "/",
    ):
        assert own_articles.link_of(refused) is None, refused


def test_title_of_is_sanitised_and_bounded():
    assert own_articles.title_of("  A​  title\n") == "A title"
    assert own_articles.title_of(None) is None
    assert own_articles.title_of("   ") is None
    assert len(own_articles.title_of("w" * 500)) == own_articles.MAX_TITLE_CHARS
