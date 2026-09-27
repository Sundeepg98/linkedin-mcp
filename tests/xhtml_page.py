"""Load a synthetic XHTML skeleton into a headless page, offline, and drive a
reader or a tool over it.

The skeletons under ``tests/fixtures/synthetic/`` built by
``scripts/_build_capture_skeleton.py`` are well-formed XHTML, and are loaded
through the browser's own XML parser (``DOMParser``) so the page is the tree
the fixture wrote, element for element. Every request the page would make is
aborted. A ``mutate`` script runs in the page after the load and before the
action: the drawings the tests use to plant a defect in the page.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Callable

import pytest

from linkedin_server import browser as browser_module

SYNTHETIC = Path(__file__).resolve().parent / "fixtures" / "synthetic"

LOADER = """(xml) => {
  const doc = new DOMParser().parseFromString(xml, 'application/xhtml+xml');
  if (doc.getElementsByTagName('parsererror').length) return -1;
  const body = doc.getElementsByTagName('body')[0];
  document.body.replaceChildren(
    ...Array.from(body.childNodes).map((node) => document.importNode(node, true)));
  return document.body.children.length;
}"""


async def with_page(fixture: Path, action: Callable[[Any], Any], *, mutate: str = "") -> Any:
    """A blank headless page, every request aborted, ``fixture`` loaded, an
    optional ``mutate`` script run in it, then ``await action(page)``."""
    playwright = pytest.importorskip("playwright.async_api")
    text = fixture.read_text(encoding="ascii")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            context = await browser.new_context()
            await context.route("**/*", lambda route: route.abort())
            page = await context.new_page()
            await page.set_content("<html><body></body></html>")
            loaded = await page.evaluate(LOADER, text)
            assert loaded and loaded > 0, f"the XML loader kept nothing of {fixture.name}"
            if mutate:
                await page.evaluate(mutate)
            return await action(page)
        finally:
            await browser.close()


def read(fixture: Path, reader: Callable[[Any], Any], *, mutate: str = "") -> Any:
    return asyncio.run(with_page(fixture, reader, mutate=mutate))


def drive_tool(fixture: Path, tool: Callable[..., Any], *, mutate: str = "",
               **arguments: Any) -> dict[str, Any]:
    """A tool end to end over the fixture: the session yields the loaded page
    and every navigation lands where it was sent without loading anything.
    The navigations are returned under ``_gotos``, in order."""
    gotos: list[str] = []

    async def run(page: Any) -> dict[str, Any]:
        @asynccontextmanager
        async def fake_session(*args: Any, **more: Any):
            yield page

        async def fake_goto(target: Any, url: str, **more: Any) -> str:
            gotos.append(url)
            return url

        original = browser_module.BROWSER.session, browser_module.BROWSER.goto
        browser_module.BROWSER.session = fake_session
        browser_module.BROWSER.goto = fake_goto
        try:
            return await tool(**arguments)
        finally:
            browser_module.BROWSER.session, browser_module.BROWSER.goto = original

    envelope = asyncio.run(with_page(fixture, run, mutate=mutate))
    envelope["_gotos"] = list(gotos)
    return envelope


def walk_strings(value: Any):
    """Every string in a returned value, keys included."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_strings(item)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            yield from walk_strings(item)


def anywhere(needle: str, value: Any) -> bool:
    return any(needle in text for text in walk_strings(value))
