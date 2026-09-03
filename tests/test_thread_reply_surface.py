"""A reply needs no address, and this is the reader that checks whether one exists.

WHY THIS SURFACE MATTERS MORE THAN THE COMPOSER. Addressing a NEW message is
the expensive problem. By NAME is a measured dead end -- eleven distinct needle
offsets across ten rows, accessible names 49 to 178 characters, so no anchored
or positional matcher can work. By IDENTIFIER works but needs an id harvested
from a page that happens to be showing one, and the viewer list yields two
usable ids from four named rows.

**A REPLY NEEDS NO ADDRESS AT ALL.** The conversation exists, the recipient is
already in it, and the recipient gate has nothing to decide. The capability
census called replying the most job-hunt-relevant messaging action in all 761
rows, and the economics agree: answering an InMail he was sent is free where
sending one spends a credit whose size this server has never been able to read.

## The one reading that would refute the whole approach

``recipient_boxes``. A thread has nobody to choose, so the expected count is
ZERO and a non-zero would mean this is not the surface it appears to be. It is
asserted first below for that reason -- an instrument whose refuting case is
buried at the bottom invites reading the confirming ones and stopping.

## Counts and booleans, and here that is not fastidiousness

A conversation page is a third party's words, in full, sent to him privately --
the richest surface in this package, richer than the profile payload, because a
payload is markup and this is correspondence. The reader has no field that
could carry a message, a name or a thread id, so there is nothing for a caller
to leak and nothing for a traceback to print.

## What these tests are

Synthetic markup, in a real browser, exercising the REAL reader. Every page
below is invented and carries no correspondence at all. **So this proves the
reader's logic and proves nothing about what LinkedIn's thread page contains**
-- that is what the probe does, and the probe refuses unless the messaging
badge reads zero first, because opening an unread conversation marks a real
person's message read.
"""

from __future__ import annotations

import pytest

from linkedin_server import dom

SEND = dom.MESSAGE_SEND_NAME
RECIPIENT_LABEL = dom.MESSAGE_RECIPIENT_LABEL


def _page(body: str) -> str:
    return "<!doctype html><html><body>" + body + "</body></html>"


#: A CONVERSATION: a reply box, a Send drawn disabled, and nobody to choose.
THREAD = _page(
    '<div contenteditable="true" role="textbox"></div>'
    f'<button disabled>{SEND}</button>'
)

#: THE SAME PAGE WITH SOMETHING TYPED. Send is enabled, which is the observable
#: transition every submit gate in this package rests on.
THREAD_TYPED = _page(
    '<div contenteditable="true" role="textbox">a reply</div>'
    f"<button>{SEND}</button>"
)

#: THE REFUTATION CASE: a composer, which DOES have somebody to choose.
COMPOSER = _page(
    f'<input role="combobox" aria-label="{RECIPIENT_LABEL}">'
    '<div contenteditable="true" role="textbox"></div>'
    f"<button disabled>{SEND}</button>"
)

#: TWO SENDS. Which one is disabled is not a question this reader may answer.
TWO_SENDS = _page(
    '<div role="textbox"></div>'
    f"<button disabled>{SEND}</button><button>{SEND}</button>"
)

#: NO SUBMIT AT ALL.
NO_SEND = _page('<div role="textbox"></div>')


async def _read(html: str):
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(
                html, wait_until="domcontentloaded", timeout=60_000
            )
            return await dom.read_thread_reply_surface(page)
        finally:
            await browser.close()


# ---------------------------------------------------------------------------
# The reading that would refute the approach, first
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_thread_offers_nobody_to_choose():
    """ZERO RECIPIENT BOXES IS THE CLAIM THE WHOLE ROUTE RESTS ON.

    If a thread drew a recipient combobox, a reply would not be addressless and
    every argument for preferring this surface over the composer would
    collapse. Asserted before anything else for that reason.
    """
    reading = await _read(THREAD)
    assert reading["error"] is None, reading["error"]
    assert reading["recipient_boxes"] == 0, reading


@pytest.mark.asyncio
async def test_the_reader_can_tell_a_composer_from_a_thread():
    """THE CONTROL, and without it the test above proves nothing.

    A reader that always returned zero recipient boxes would pass the
    refutation test perfectly while being blind. The composer draws one, and
    this reads one.
    """
    reading = await _read(COMPOSER)
    assert reading["recipient_boxes"] == 1, reading


# ---------------------------------------------------------------------------
# The reply box and the gate signal
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_it_finds_the_reply_box_under_both_spellings():
    """TWO SPELLINGS BECAUSE A LINKEDIN EDITOR HAS BEEN MEASURED AS BOTH.

    A reader that knew only ``contenteditable`` would report zero on a page
    that uses ``role=textbox``, and vice versa -- and a zero from a reader that
    cannot see is indistinguishable from a page with no reply box.
    """
    reading = await _read(THREAD)
    assert reading["editors"] == 1, reading
    assert reading["textboxes"] == 1, reading


@pytest.mark.asyncio
async def test_send_is_disabled_on_an_empty_reply_and_enabled_on_a_typed_one():
    """THE TRANSITION, ASSERTED IN BOTH DIRECTIONS.

    "Send is disabled" alone would pass against a reader that always said
    disabled. The pair is what makes it a measurement: the same page with
    something in the box reads enabled.
    """
    empty = await _read(THREAD)
    typed = await _read(THREAD_TYPED)
    assert empty["send_controls"] == 1, empty
    assert empty["send_disabled"] is True, empty
    assert typed["send_disabled"] is False, typed


# ---------------------------------------------------------------------------
# Absent is not False
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_two_sends_leave_the_disabled_question_unasked():
    """NOT ASKED IS NOT FALSE, and collapsing them removes a test.

    With two controls named Send, asking whether "the" one is disabled reads
    whichever Playwright resolved first -- an answer by document order. The
    reader returns None, which says the question was not put, and a caller can
    tell that from an answer of False.
    """
    reading = await _read(TWO_SENDS)
    assert reading["send_controls"] == 2, reading
    assert reading["send_disabled"] is None, reading


@pytest.mark.asyncio
async def test_no_send_control_is_reported_as_none_rather_than_true():
    """A page with no submit has not got a DISABLED submit."""
    reading = await _read(NO_SEND)
    assert reading["send_controls"] == 0, reading
    assert reading["send_disabled"] is None, reading


# ---------------------------------------------------------------------------
# It emits nothing that could carry correspondence
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_reading_carries_no_text_from_the_page():
    """THE SURFACE IS SOMEBODY'S PRIVATE CORRESPONDENCE.

    The typed page holds a message. Every value the reader returns is asserted
    to be an int, a bool or None -- so there is no field a message, a name or a
    thread id could travel in, which is a stronger property than a guard that
    strips them afterwards.
    """
    reading = await _read(THREAD_TYPED)
    assert reading.pop("error") is None
    for key, value in reading.items():
        assert isinstance(value, (int, bool)) or value is None, (key, value)
    assert "a reply" not in repr(reading)


def test_the_reader_has_no_output_path_and_no_logging():
    """Asserted on the source, because a docstring promising restraint is the
    class of claim this repository converts into a check."""
    import inspect

    source = inspect.getsource(dom.read_thread_reply_surface)
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    for sink in ("logger.", "print(", "open(", ".write_text("):
        assert sink not in code, sink
