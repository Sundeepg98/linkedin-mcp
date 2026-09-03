"""A redaction applied at one site and not at the site beside it.

WHAT HAPPENED. On 2026-09-03 a live `linkedin_open_messaging` reading put a
REAL conversation identifier into a transcript. Its twin, in the same result
block, was correctly redacted:

    thread_opened.landed_url   ".../messaging/thread/<THREAD-ID>/"   safe
    active_filter.url_before   the whole id                          RAW
    active_filter.url_after    the whole id, plus ?filter=inmail     RAW

``shape.redact_thread_id`` existed and worked. It was applied to the first
field and not to the pair added later, by somebody reading the first as
decoration rather than as a guard.

## Why no existing instrument caught it, which is the part worth keeping

``tests/test_navigation_is_never_derived.py`` guards two SINKS: a value the
browser produced reaching a NAVIGATION, and one reaching a PRINT. **This value
reached neither.** It was RETURNED, as data, and travelled to a model's context
that way.

> **A returned identifier is a third sink, and the taint rule does not model
> it.** Naming that is worth more than the fix: every reader in this package
> returns data to a caller, so the sink the rule does not cover is the one
> every reader uses.

``test_no_committed_identity`` did not catch it either, and correctly -- it
scans FILES, and this identifier was never written to one.

## What this file checks

The CLASS, not the instance. Every value ``activate_messaging_filter`` returns
is asserted to carry no raw thread id, so a THIRD url field added tomorrow
fails here rather than shipping raw. Checking the two known fields by name
would protect the two mistakes already made and none of the next one.

**AND IT IS FIXED AT THE SOURCE.** A caller-side redaction leaves the raw value
on the next caller; nothing that consumes this function can leak what it never
receives.
"""

from __future__ import annotations

import re

import pytest

from linkedin_server import dom, shape

#: A thread id shaped like the real one, invented. Base64-ish with the digit
#: prefix and the padding that made the live value unmistakable.
FAKE_THREAD_ID = "2-INVENTEDTHREADIDzzz=="
THREAD_URL = f"https://www.linkedin.com/messaging/thread/{FAKE_THREAD_ID}/"

#: A url is UNREDACTED if a thread segment survives that is not the marker.
RAW_THREAD = re.compile(r"/messaging/thread/(?!<THREAD-ID>)[^/?#]+")


class _Pills:
    def __init__(self, count: int) -> None:
        self._count = count

    async def count(self) -> int:
        return self._count

    @property
    def first(self):
        return self

    async def get_attribute(self, _name: str) -> str:
        return "InMail"

    async def click(self, **_kw) -> None:
        return None

    async def inner_text(self) -> str:
        return "InMail"


class _Page:
    """A page whose url is a REAL-SHAPED thread url before and after."""

    def __init__(self, url: str, pill_count: int = 1) -> None:
        self.url = url
        self._pills = _Pills(pill_count)

    def get_by_role(self, *_a, **_kw):
        return self._pills

    async def wait_for_timeout(self, _ms: int) -> None:
        return None


@pytest.mark.asyncio
async def test_no_value_it_returns_carries_a_raw_thread_id():
    """THE CLASS. Every returned value, not the two fields that were wrong.

    A third url field added tomorrow fails here. Checking `url_before` and
    `url_after` by name would protect exactly the two mistakes already made.
    """
    result = await dom.activate_messaging_filter(_Page(THREAD_URL), "inmail")
    assert result["activated"] is True, result
    for key, value in result.items():
        if isinstance(value, str):
            assert not RAW_THREAD.search(value), (key, "carries a raw thread id")
    assert FAKE_THREAD_ID not in repr(result), result


@pytest.mark.asyncio
async def test_the_two_url_fields_are_redacted_and_still_present():
    """REDACTED, NOT DROPPED.

    Deleting the fields would also pass the test above and would remove the
    only evidence a caller has that the click navigated. The marker has to be
    THERE.
    """
    result = await dom.activate_messaging_filter(_Page(THREAD_URL), "inmail")
    assert "<THREAD-ID>" in result["url_before"], result["url_before"]
    assert "<THREAD-ID>" in result["url_after"], result["url_after"]


@pytest.mark.asyncio
async def test_the_navigated_signal_survives_redaction():
    """THE SIGNAL A CALLER ACTUALLY NEEDS IS A BOOLEAN.

    `navigated` compares the urls BEFORE redaction, so it still answers the
    question the two fields exist for -- and a comparison yields a boolean,
    which carries nothing. That is why redacting the pair costs the caller
    nothing at all.
    """
    same = await dom.activate_messaging_filter(_Page(THREAD_URL), "inmail")
    assert same["navigated"] is False, same


def test_the_redactor_is_shown_working_and_shown_not_over_reaching():
    """BOTH DIRECTIONS. A redactor that flattened every url would pass a
    leak-only test perfectly while destroying every other reading."""
    assert "<THREAD-ID>" in shape.redact_thread_id(THREAD_URL)
    assert FAKE_THREAD_ID not in shape.redact_thread_id(THREAD_URL)
    # NOT a thread url: it must come back untouched.
    feed = "https://www.linkedin.com/feed/"
    assert shape.redact_thread_id(feed) == feed
    profile = "https://www.linkedin.com/in/some-slug/"
    assert shape.redact_thread_id(profile) == profile


def test_the_pattern_this_file_guards_with_can_fail():
    """A DETECTOR THAT CANNOT FIRE CERTIFIES NOTHING.

    Asserted directly: the raw url matches, the redacted one does not. Without
    this, a regex typo would make every assertion above vacuously true.
    """
    assert RAW_THREAD.search(THREAD_URL)
    assert not RAW_THREAD.search(shape.redact_thread_id(THREAD_URL))
