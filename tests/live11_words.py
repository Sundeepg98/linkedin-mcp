"""Shared helpers for lane readers-jobs26's tests over session 11's word skeletons.

The fixtures are ``tests/fixtures/live11/*_words.html``, each built by
``scripts/_build_live11_word_skeletons.py`` from the live lane's session-11
keyed skeleton: the committed tracked copy, with LinkedIn's own interface words
written only where their keyed shapes matched. Every other text is ``x``.

Two ways a test reads one:

* :func:`chromium_page` -- a LOCAL headless Chromium whose page serves itself
  nothing from outside: the skeleton keeps the capture's stylesheet and image
  addresses (reduced to ``https://x/...``), and every request they would start
  is aborted by the page's own route, before the network guard has to.
* :func:`skeleton` -- the parsed document behind ``tests/skeleton_page.py``,
  for a locator-only reader, with no browser.

:func:`plant` is an ASSERTED edit: a replace whose anchor drifted is a silent
no-op otherwise, and a plant that changes nothing proves nothing.

Every name-shaped string a test plants is synthetic.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "live11"


def words(stem: str) -> str:
    """The text of ``tests/fixtures/live11/<stem>_words.html``."""
    return (FIXTURES / (stem + "_words.html")).read_text(encoding="ascii")


def plain(stem: str) -> str:
    """The text of the committed tracked copy, its words reduced."""
    return (FIXTURES / (stem + ".html")).read_text(encoding="ascii")


def plant(markup: str, old: str, new: str, count: int = 1) -> str:
    """Replace ``old`` by ``new`` in the MARKUP -- never in a words fixture's
    provenance comment, which lists the words -- exactly ``count`` times, and
    fail the test unless the markup draws ``old`` exactly that many times."""
    marker = "\n-->\n"
    head, sep, body = markup.partition(marker) if marker in markup else ("", "", markup)
    assert body.count(old) == count, (
        "the fixture draws what this plant edits %d time(s), not %d" % (body.count(old), count)
    )
    return head + sep + body.replace(old, new)


def body_lines(fixture_text: str) -> list[str]:
    """The fixture's lines after its provenance comment, for a comparison with
    the committed copy's lines after its doctype."""
    marker = "\n-->\n"
    assert marker in fixture_text, "a words fixture opens with its provenance comment"
    return fixture_text.split(marker, 1)[1].split("\n")


@pytest.fixture
async def chromium_page():
    """A local headless Chromium page that refuses every request it would make."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()

            async def _refuse(route):  # noqa: ANN001 - a playwright route
                await route.abort()

            await page.route("**/*", _refuse)
            yield page
        finally:
            await browser.close()
