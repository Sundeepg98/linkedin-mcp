"""A navigation that FAILS names its exception type -- never the address it tried.

``LinkedInBrowser.goto`` composes nothing, but the address it is handed often
carries the CALLER's words: a search keyword, a member token, an id he named.
Until the lane G follow-up of 2026-09-24 its failure raised

    BrowserUnavailableError(f"navigation to {url} failed: {type(exc).__name__}: {exc}")

-- the address twice over, since a Playwright navigation error quotes it again
-- and ``server._error`` publishes that message as ``$.message``, into the
tool's answer and whatever transcript holds it. Found by lane S.

The decision is taken where the value enters the exception
(``ERROR-MESSAGE-RULED-AT-THE-RAISE``): the message carries the exception's
TYPE and the address's first path segment -- a family, never a keyword or a
member token -- and the original stays chained in-process for a debugger.
"""
from __future__ import annotations

import json

import pytest

from linkedin_server import readonly, server
from linkedin_server.browser import LinkedInBrowser
from linkedin_server.errors import BrowserUnavailableError

#: What the caller "searched for". Not a name and not anybody's token.
KEYWORD = "example-caller-keyword"

ADMITTED = (
    "https://www.linkedin.com/jobs/search/?keywords=" + KEYWORD,
    "https://www.linkedin.com/search/results/people/?keywords=" + KEYWORD,
)


class _FailingPage:
    """A page whose navigation fails the way Playwright's does: quoting it."""

    async def goto(self, target, **kwargs):
        raise TimeoutError(f"Timeout 30000ms exceeded navigating to {target}")


@pytest.mark.parametrize("url", ADMITTED)
async def test_a_failed_navigation_names_its_type_and_withholds_the_address(url):
    assert readonly.is_read_url(url), (
        f"precondition: {url} must be an admitted read, or goto refuses before "
        "navigating and this test measures the allowlist instead"
    )
    browser = LinkedInBrowser()

    with pytest.raises(BrowserUnavailableError) as caught:
        await browser.goto(_FailingPage(), url)

    text = str(caught.value)
    assert "TimeoutError" in text, text
    assert KEYWORD not in text, text
    assert "linkedin.com" not in text, text
    assert "?" not in text, text
    # THE ENVELOPE, too -- it is where the message goes next.
    envelope = json.dumps(server._error(caught.value))
    assert KEYWORD not in envelope, envelope
    # AND THE CAUSE IS KEPT, in-process only, for whoever debugs it.
    assert isinstance(caught.value.__cause__, TimeoutError)


async def test_the_family_it_names_is_the_first_path_segment_only():
    """What the message MAY say about the address: which family, nothing else."""
    browser = LinkedInBrowser()
    with pytest.raises(BrowserUnavailableError) as caught:
        await browser.goto(_FailingPage(), ADMITTED[0])
    assert "/jobs/" in str(caught.value), str(caught.value)
    assert "/search/" not in str(caught.value), str(caught.value)
