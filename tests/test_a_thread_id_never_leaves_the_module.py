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
#: prefix and the padding that made the live value unmistakable. ITS SHAPE IS
#: DECORATION and may be changed freely: the redactor matches ``[^/?#]+``, so
#: any non-empty run without a delimiter exercises it identically. That is
#: NOT true of the slug below, which is the distinction this file now pins.
FAKE_THREAD_ID = "2-INVENTEDTHREADIDzzz=="
THREAD_URL = f"https://www.linkedin.com/messaging/thread/{FAKE_THREAD_ID}/"

#: A member profile url, and THE ONE LITERAL HERE WHOSE SHAPE IS LOAD-BEARING.
#: It is the over-reach control: a redactor that flattened every url would
#: pass a leak-only test perfectly while destroying every profile reading, and
#: this url is what notices. The mutant that does that is keyed on SLUG SHAPE,
#: so an unmistakable placeholder -- ``/in/<SLUG>`` -- would not match it, the
#: assertion would hold under the mutant, and the control would quietly stop
#: being able to fire. Measured both ways in
#: ``test_the_profile_control_is_load_bearing``, which is why that test exists
#: instead of this comment being trusted.
#:
#: WHY THIS PARTICULAR VALUE IS SAFE, so nobody re-derives it: the slug is
#: already sanctioned in ``SYNTHETIC_SLUGS`` in
#: ``tests/test_no_committed_identity.py`` -- shape-valid, unmistakably
#: fabricated, and blessed there rather than declared here, so no allowlist
#: moves and no plant has to be pinned. THIS FILE SHIPPED WITH ``some-slug``
#: INSTEAD, and that guard failed it within the hour: a hand-written
#: placeholder is not the same thing as a declared one, because the guard has
#: no way to tell it from a real slug. Reusing an allowlisted value is what
#: makes the literal both safe and load-bearing at once.
PROFILE_URL = "https://www.linkedin.com/in/some-person-a1b2c3/"

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

    async def get_attribute(self, _name: str, timeout=None, **_kwargs) -> str:
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
    assert shape.redact_thread_id(PROFILE_URL) == PROFILE_URL


#: THE MUTANT THE PROFILE CONTROL EXISTS TO CATCH: somebody reads
#: ``redact_thread_id`` as "the redactor" and generalises it to every url that
#: names a member. The character class is the identity guard's own
#: ``SLUG_SHAPE``, so "shape-valid" here means valid by the repo's definition
#: of the shape rather than by one invented in this file.
_OVER_REACHING_SLUG = re.compile(r"(/in/)([A-Za-z0-9\-_%]{3,})")


def _over_reaching_redactor(url: str) -> str:
    """``redact_thread_id`` as it must NOT become."""
    url = re.sub(r"(/messaging/thread/)[^/?#]+", r"\1<THREAD-ID>", url)
    return _OVER_REACHING_SLUG.sub(r"\1<SLUG>", url)


def test_the_profile_control_is_load_bearing():
    """The profile url's SHAPE is what lets the over-reach control fail.

    WHY THIS IS A TEST AND NOT A COMMENT. A slug-shaped literal in a tracked
    file is a cost -- the identity guard has to be able to tell it from a real
    one -- so it has to earn its place, and "trust me, it is needed" is what a
    comment offers. This measures it.

    IT GUARDS THE SWAP THAT LOOKS FREE. ``redact_thread_id`` reads no slug
    shape at all, so replacing the slug with ``<SLUG>`` raises nothing and
    fails nothing today. What it does is make the mutant below invisible:
    ``<SLUG>`` is not slug-shaped, the over-reaching redactor leaves it alone,
    ``redact_thread_id(PROFILE_URL) == PROFILE_URL`` holds under the mutant
    too, and an assertion that cannot fail is left behind looking like
    coverage. Both directions are asserted, because only the pair shows that
    the shape -- and not the url -- is doing the work.
    """
    # The control CAN fail: the mutant changes the value it asserts is equal.
    assert _over_reaching_redactor(PROFILE_URL) != PROFILE_URL, (
        "the over-reaching redactor no longer touches PROFILE_URL, so the "
        "second assertion in the not-over-reaching test certifies nothing"
    )
    # And a placeholder is exactly what would kill it.
    placeholder = "https://www.linkedin.com/in/<SLUG>/"
    assert _over_reaching_redactor(placeholder) == placeholder, (
        "a placeholder slug is now matched by the mutant, which would make "
        "the swap safe after all -- re-read this test before relying on it"
    )
    # The mutant is otherwise the shipped redactor: it must still redact
    # threads, or the two assertions above would pass on a dead function.
    assert "<THREAD-ID>" in _over_reaching_redactor(THREAD_URL)


def test_the_pattern_this_file_guards_with_can_fail():
    """A DETECTOR THAT CANNOT FIRE CERTIFIES NOTHING.

    Asserted directly: the raw url matches, the redacted one does not. Without
    this, a regex typo would make every assertion above vacuously true.
    """
    assert RAW_THREAD.search(THREAD_URL)
    assert not RAW_THREAD.search(shape.redact_thread_id(THREAD_URL))
