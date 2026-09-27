"""The network guard, shown refusing, shown failing a test by name, shown
letting local pages through.

``tests/network_guard.py`` is what makes ``tests/conftest.py``'s first
sentence true. A guard that has never been seen refusing certifies nothing, so
each half is driven here in a real headless Chromium:

* a planted request to an address off this machine is REFUSED before it
  leaves -- the page sees ``net::ERR_BLOCKED_BY_CLIENT``, which only the
  guard's abort produces -- and recorded against the test that made it;
* a test that makes one FAILS, LOUDLY, naming itself and the address -- shown
  in a separate pytest process, because failing is the point;
* a loopback request, and a page a test serves itself through ``page.route``,
  are NOT refused: the guard is about leaving the machine, not about loading
  pages.

THE PLANTED ADDRESS IS ``.invalid``, a name that can never resolve (RFC 6761),
so a guard that stopped working would still send nothing anywhere -- and the
error the page sees then would be a DNS failure, not the guard's, which is
what the refusal assertion tells apart.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests import network_guard

REPO = Path(__file__).resolve().parents[1]

#: Never resolvable, anywhere.
PLANTED = "https://network-guard-plant.invalid/planted"


def _playwright():
    return pytest.importorskip("playwright.async_api")


def test_the_guard_is_registered_in_this_run_with_no_flag(request):
    """``tests/conftest.py`` registers it, so every run -- CI's, a lane's, a
    single file's -- has it, and nobody has to remember a flag."""
    assert request.config.pluginmanager.hasplugin("tests.network_guard")


@pytest.mark.parametrize(
    "url, local",
    [
        ("https://www.linkedin.com/jobs/view/1/apply/", False),
        ("https://media.licdn.com/x.png", False),
        ("http://example.com/", False),
        (PLANTED, False),
        ("http://127.0.0.1:9/", True),
        ("http://localhost:8765/page", True),
        ("http://[::1]:9/", True),
        ("about:blank", True),
        ("data:text/html,<p>x</p>", True),
        ("blob:null/1234", True),
        ("file:///tmp/page.html", True),
        ("chrome-error://chromewebdata/", True),
    ],
)
def test_what_counts_as_local(url, local):
    assert network_guard.is_local(url) is local


async def test_a_planted_request_is_refused_before_it_leaves():
    """THE REFUSAL. The page asks for an address off this machine; the guard
    aborts it with its own error and records it. The record is taken here,
    so this test does not fail for the request it set out to make."""
    pw_module = _playwright()
    network_guard.take_refused()
    async with pw_module.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            with pytest.raises(pw_module.Error) as refused:
                await page.goto(PLANTED, timeout=15_000)
        finally:
            await browser.close()
    assert "ERR_BLOCKED_BY_CLIENT" in str(refused.value), (
        "the request failed, but not by the guard's abort -- a DNS failure reads "
        "ERR_NAME_NOT_RESOLVED -- so the guard did not see it: %s" % refused.value
    )
    taken = network_guard.take_refused()
    assert [url for _nodeid, url in taken] == [PLANTED], taken
    assert all(nodeid.endswith(
        "test_a_planted_request_is_refused_before_it_leaves") for nodeid, _url in taken), taken


async def test_a_context_the_test_opens_itself_is_guarded_too():
    """``new_context`` as well as ``new_page``: the two ways the suite opens
    pages, and neither may leave the machine."""
    pw_module = _playwright()
    network_guard.take_refused()
    async with pw_module.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            context = await browser.new_context()
            page = await context.new_page()
            with pytest.raises(pw_module.Error) as refused:
                await page.goto(PLANTED, timeout=15_000)
        finally:
            await browser.close()
    assert "ERR_BLOCKED_BY_CLIENT" in str(refused.value), refused.value
    assert [url for _nodeid, url in network_guard.take_refused()] == [PLANTED]


async def test_loopback_and_a_page_the_test_serves_are_not_refused():
    """NOT A BAN ON LOADING PAGES: a loopback request goes through -- nothing
    listens on port 9, so it is refused by the CONNECTION, not the guard --
    and a LinkedIn address the test answers itself through ``page.route`` is
    served, because a page's route outranks the guard's. Neither is recorded."""
    pw_module = _playwright()
    network_guard.take_refused()
    async with pw_module.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            loopback = await browser.new_page()
            with pytest.raises(pw_module.Error) as closed_port:
                await loopback.goto("http://127.0.0.1:9/nothing-listens", timeout=15_000)

            async def serve(route):
                await route.fulfill(status=200, content_type="text/html",
                                    body="<p id=served>served here</p>")

            page = await browser.new_page()
            await page.route("https://www.linkedin.com/**", serve)
            await page.goto("https://www.linkedin.com/served-locally", timeout=15_000)
            served = await page.inner_text("#served")
        finally:
            await browser.close()
    assert "ERR_BLOCKED_BY_CLIENT" not in str(closed_port.value), closed_port.value
    assert served == "served here"
    assert network_guard.take_refused() == []


_A_TEST_THAT_REACHES_OUT = '''
import asyncio

from playwright.async_api import async_playwright


def test_it_reaches_out():
    async def main():
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                try:
                    await page.goto("%s", timeout=15000)
                except Exception:
                    pass
            finally:
                await browser.close()

    asyncio.run(main())
''' % PLANTED


def test_a_test_that_reaches_out_fails_loudly_by_name(tmp_path):
    """THE LOUD HALF, in its own pytest process with only the guard loaded: a
    test that swallows its own error still FAILS, and the failure names the
    test and the address."""
    pytest.importorskip("playwright.async_api")
    planted = tmp_path / "test_reaches_out.py"
    planted.write_text(_A_TEST_THAT_REACHES_OUT, encoding="ascii")
    env = dict(os.environ, PYTHONPATH=str(REPO))
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "tests.network_guard", "-p", "no:cacheprovider",
         "-q", "-o", "addopts=", "--rootdir", str(tmp_path), str(planted)],
        cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=180,
    )
    output = done.stdout + done.stderr
    assert done.returncode == 1, output[-2000:]
    assert "1 failed" in output, output[-2000:]
    assert "test_reaches_out.py::test_it_reaches_out REACHED FOR THE NETWORK" in output, output[-2000:]
    assert PLANTED in output, output[-2000:]
