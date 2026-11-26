"""THE FIRST OPENED CONVERSATION ON DISK DRAWS NO VIDEO-MEETING CONTROL -- read
offline, every control of its reply form accounted for, and shown able to see
one if a page drew it.

THE CAPTURE. Live session 11, load 40 (2026-11-26): the conversation he named,
opened by its recorded id behind the receipt guard at 0 unread, its tracked
skeleton ``tests/fixtures/live11/msg_thread.html``. The live lane's own reading
of the footer at capture time: 7 buttons, 5 named in LinkedIn's furniture words,
2 others, 0 video-meeting controls, 0 suggestion nodes, 1 editor.

THE READING THE CENSUS MOVE RESTS ON (census ``M M20``, MEASURED-ABSENT under
MEASURED-ABSENT-OR-PRECONDITION): the reply form's seven controls are, by
STRUCTURE, the two attachment buttons (each wrapped with its own file input),
the GIF and emoji keyboards, the editor's maximize toggle, Send and the send
options toggle -- so no control in the form is left that could be a meeting
control -- and the conversation's header draws its menu and its star. The two
attachment buttons' labels are reduced to ``x`` in the tracked copy; that they
are attachments is read off the file input each one shares a wrapper with,
never off a word.

THE AI MODULE (census ``M M51``). The form draws ``msg-gai-inline-module``
inside its own container, EMPTY on this conversation -- whose last message is
his own. What it draws for a conversation whose last message is the other
member's is the next capture's question, not this file's.

EVERY BROWSER HERE IS HEADLESS AND LOADS NOTHING: each page aborts every
network request. Nothing is pressed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

from linkedin_server import threads

IN_MODULE_LOOP = pytest.mark.asyncio(loop_scope="module")


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def _browser():
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


@pytest_asyncio.fixture(loop_scope="module")
async def page(_browser):
    context = await _browser.new_context()
    try:
        yield await context.new_page()
    finally:
        await context.close()


THREAD = (Path(__file__).resolve().parent / "fixtures" / "live11" / "msg_thread.html").read_text(
    encoding="ascii"
)

#: Every control of the reply form, each by the STRUCTURE that names it --
#: never a label, since the tracked copy keeps only LinkedIn's furniture words.
#: An attachment button is the one button inside a wrapper that also holds a
#: file input; the rest carry LinkedIn's own words or their own classes.
ACCOUNTING = """() => {
  const form = document.querySelector('main form.msg-form');
  if (!form) return null;
  const buttons = Array.from(form.querySelectorAll('button'));
  const out = {buttons: buttons.length, attachment: 0, gif: 0, emoji: 0, maximize: 0,
               send: 0, send_options: 0, unaccounted: 0};
  for (const b of buttons) {
    const label = (b.getAttribute('aria-label') || b.textContent || '').trim();
    const wrapper = b.parentElement;
    if (wrapper && wrapper.querySelectorAll('input[type="file"]').length === 1
        && wrapper.querySelectorAll('button').length === 1) out.attachment += 1;
    else if (label === 'Open GIF Keyboard') out.gif += 1;
    else if (label === 'Open Emoji Keyboard') out.emoji += 1;
    else if (label === 'Maximize compose field') out.maximize += 1;
    else if (b.type === 'submit' && label === 'Send') out.send += 1;
    else if (label === 'Open send options') out.send_options += 1;
    else out.unaccounted += 1;
  }
  const gai = form.querySelectorAll('.msg-gai-inline-module');
  out.ai_modules = gai.length;
  out.ai_module_children = gai.length === 1 ? gai[0].querySelectorAll('*').length : null;
  const bar = document.querySelector('main .msg-title-bar');
  out.header_buttons = bar ? bar.querySelectorAll('button').length : null;
  out.header_menus = bar ? bar.querySelectorAll('button[aria-expanded]').length : null;
  return out;
}"""

#: A meeting control as a page might draw one: a footer action with its own
#: words. Planted to show the two readings CAN see one.
MEETING = (
    "() => { const f = document.querySelector('main form.msg-form .msg-form__left-actions');"
    " const b = document.createElement('button'); b.type = 'button';"
    " b.className = 'msg-form__footer-action';"
    " b.setAttribute('aria-label', 'Create a video meeting'); f.appendChild(b); }"
)


async def _load(page: Any, mutate: str = "") -> None:
    async def _refuse(route: Any) -> None:
        await route.abort()

    await page.route("**/*", _refuse)
    await page.set_content(THREAD, wait_until="domcontentloaded")
    if mutate:
        await page.evaluate(mutate)


@IN_MODULE_LOOP
async def test_the_shipped_thread_reader_sees_the_footer_and_no_meeting_control(page):
    await _load(page)
    reading = await threads.read_thread(page)
    assert reading["error"] is None and reading["rendered"] is True
    assert reading["forms"] == 1 and reading["editors"] == 1 and reading["send_controls"] == 1
    assert reading["file_inputs"] == 2
    assert reading["footer_actions"] == ["unrecognised", "unrecognised", "gif_keyboard", "emoji_keyboard"]
    assert "video_meeting" not in reading["footer_actions"]
    # His own last message: the side a suggested reply would answer is not drawn.
    assert reading["items_from_the_other_side"] == 0


@IN_MODULE_LOOP
async def test_every_control_of_the_reply_form_is_accounted_for_by_structure(page):
    await _load(page)
    counted = await page.evaluate(ACCOUNTING)
    assert counted == {
        "buttons": 7, "attachment": 2, "gif": 1, "emoji": 1, "maximize": 1,
        "send": 1, "send_options": 1, "unaccounted": 0,
        "ai_modules": 1, "ai_module_children": 0,
        "header_buttons": 2, "header_menus": 1,
    }


@IN_MODULE_LOOP
async def test_THIS_CONTROL_CAN_FAIL_a_meeting_control_drawn_is_seen_by_both_readings(page):
    await _load(page, mutate=MEETING)
    reading = await threads.read_thread(page)
    assert "video_meeting" in reading["footer_actions"]
    counted = await page.evaluate(ACCOUNTING)
    assert counted["unaccounted"] == 1 and counted["buttons"] == 8


@IN_MODULE_LOOP
async def test_THIS_CONTROL_CAN_FAIL_a_button_without_a_file_input_is_not_an_attachment(page):
    """The structural rule, not the count, decides: take one file input away
    and its button is no longer accounted for."""
    await _load(page, mutate=(
        "() => { document.querySelector('main form.msg-form input[type=\"file\"]').remove(); }"
    ))
    counted = await page.evaluate(ACCOUNTING)
    assert counted["attachment"] == 1 and counted["unaccounted"] == 1
