"""Five surfaces, one answer: `contenteditable == 0`. Is that the page or the reader?

THE FINDING THAT PROMPTED THIS. Every surface this package has measured reports
zero ``contenteditable`` nodes -- the feed, the profile, the post composer, the
comment surface, and now an open message thread -- on pages where a human
plainly types. The package's own prose calls that "the standing measurement on
every surface". **Five surfaces agreeing is no longer a fact about any one of
them.** It is a fact about the reader, or about LinkedIn, and nobody has
distinguished those two.

Until somebody does, EVERY typing capability here is blocked on one unexamined
assumption, and the compose route is about to return the same zero for the same
reason.

## Four hypotheses, and they are not equally likely

**1. THE EDITOR IS A ``<textarea>`` AND NO READER LOOKS FOR ONE.** This is the
cheapest and it is checked first, because it is embarrassing rather than
exotic. ``read_thread_reply_surface`` counts ``[contenteditable]`` and
``[role=textbox]`` and nothing else -- while ``dom.py`` elsewhere knows
perfectly well that textareas exist and handles them in two other scripts. A
whole class of editor is simply outside every editor-reader's aim.

**2. IT IS INSIDE AN IFRAME.** A locator only searches the frame it was made
on, so a main-frame count cannot see one. Each frame is counted separately
here.

**3. IT ARRIVES AFTER THE SETTLE.** The counts are taken twice, with a wait
between, so "not yet" and "not there" stop being the same zero.

**4. IT IS IN A CLOSED SHADOW ROOT.** Checked last and expected to be
unlikely: **Playwright's CSS engine already pierces OPEN shadow roots**, so a
zero from the main frame has already ruled out the common case. Only a CLOSED
root would hide from it, and closed roots are rare in application code.

## What it emits

COUNTS AND A FRAME INDEX. Never a frame url -- a messaging frame's url carries
the conversation id, which is the exact value that reached a transcript today
and had to be redacted at source. There is no field here that could carry one.

## Bounds

ONE NAVIGATION, to ``config.MESSAGING_URL``, a module constant -- nothing
derived from a landed url, so the taint rule that exists because of that defect
is satisfied by construction.

NO ``page.evaluate`` ANYWHERE. Every count is a Playwright locator, which is
why this script needs no ``# readonly-ok`` waiver and adds nothing to the
budget ``tests/test_readonly.py`` pins. It also means the shadow-piercing above
is Playwright's, not a hand-rolled DOM walk that would need its own correctness
argument.

THE BADGE MUST READ ZERO. Opening messaging opens a conversation LinkedIn
chooses, and opening an unread one marks a real person's message read. An
UNREADABLE badge refuses too: unknown is not permission.

Run:  python scripts/_probe_where_the_editor_lives.py
Writes NOTHING. Presses nothing. Types nothing.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL, MESSAGING_URL  # noqa: E402

#: EVERY MECHANISM AN EDITOR COULD BE, counted separately so the answer names
#: one rather than reporting a total nobody can act on.
#:
#: ``textarea`` and the text inputs are here because they are the hypothesis no
#: existing reader tests. ``[contenteditable]`` is split from
#: ``[contenteditable="true"]`` because the bare attribute selector matches
#: ``contenteditable="false"`` too, and a reader that conflated them would
#: report an editor that refuses input.
MECHANISMS: tuple[tuple[str, str], ...] = (
    ("contenteditable, any value", "[contenteditable]"),
    ("contenteditable=true", '[contenteditable="true"]'),
    ("role=textbox", '[role="textbox"]'),
    ("textarea", "textarea"),
    ("input type=text", 'input[type="text"]'),
    ("input, any type", "input"),
    ("ALL elements (liveness)", "*"),
)

#: How long to wait before the second reading. Generous: the question is
#: whether the editor EVER arrives, not how fast.
LATE_HYDRATION_WAIT_MS = 8_000


async def _census(frame) -> dict[str, int]:
    """Count every mechanism in one frame. Counts only; no url, no text."""
    out: dict[str, int] = {}
    for label, selector in MECHANISMS:
        try:
            out[label] = int(await frame.locator(selector).count())
        except Exception as exc:  # noqa: BLE001 - a -1 is a reading
            out[label] = -1
            del exc
    return out


def _show(title: str, counts: dict[str, int]) -> None:
    print(f"    {title}")
    for label, _selector in MECHANISMS:
        print(f"      {counts.get(label, -1):6d}  {label}")


async def main() -> None:
    print("=== WHERE DOES THE EDITOR LIVE?")
    print("    one navigation, nothing pressed, counts and frame indexes only\n")

    await BROWSER.start()
    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, FEED_URL)
        if "/login" in landed or "/checkpoint" in landed:
            print("    AUTH WALL. Not signed in, so nothing was measured.")
            await BROWSER.stop()
            return
        # THE BADGE, THROUGH THE READER THAT INTERPRETS IT.
        #
        # THIS GATE COULD NEVER HAVE PASSED, and the first live run refused
        # because of it rather than because of the badge. It called
        # `dom.read_messaging_badge`, which returns {"links", "label"} -- a raw
        # reading -- and then asked it for `unread` and `readable`, TWO FIELD
        # NAMES THAT DO NOT EXIST ON IT. Both came back None from `.get`, so
        # the refusal fired unconditionally, on every run, forever.
        #
        # A precondition that is unsatisfiable BY CONSTRUCTION is the same
        # shape as a guard that cannot fire: present, correct-looking, and
        # structurally unable to do its job. It looked like an unreadable page.
        #
        # THE INTERPRETATION LIVES IN `shape.messaging_badge`, which is what
        # `linkedin_new_messages` uses and why that tool read 0 from the same
        # badge, the same account and the same session twelve minutes earlier.
        # Reaching for the raw reader meant inventing a second interpretation,
        # and the one I invented was wrong.
        #
        # ITS `why` DISTINGUISHES THE TWO FAILURES -- no badge element found,
        # versus found and unparseable -- which is the thing the old refusal
        # could not say and which cost two wrong diagnoses today.
        html = await page.content()
        badge = shape.messaging_badge(html)
        print(
            "    messaging badge: new_since_last_visit="
            f"{badge.get('new_since_last_visit')!r} state={badge.get('state')!r}"
        )
        print(f"    why: {badge.get('why')}")
        if badge.get("state") != "read":
            print("    REFUSED: the badge could not be read. Unknown is not")
            print("    permission -- this cannot tell whether opening")
            print("    messaging would mark somebody's message read.")
            await BROWSER.stop()
            return
        if badge.get("new_since_last_visit"):
            print("    REFUSED: unread messages. Opening messaging would mark")
            print("    a real person's message read.")
            await BROWSER.stop()
            return

        thread_landed = await BROWSER.goto(page, MESSAGING_URL)
        print(
            f"    landed inside a conversation: "
            f"{'/messaging/thread/' in thread_landed}\n"
        )

        print("=== READING ONE, IMMEDIATELY AFTER THE SETTLE")
        _show("main frame:", await _census(page))

        frames = list(page.frames)
        print(f"\n    frames on this page: {len(frames)} (including the main one)")
        print("    (frame URLS are never printed -- a messaging frame's url")
        print("     carries the conversation id.)")
        for index, frame in enumerate(frames):
            if index == 0:
                continue
            print()
            _show(f"frame #{index}:", await _census(frame))

        print(f"\n=== READING TWO, AFTER {LATE_HYDRATION_WAIT_MS}ms")
        print("    Same page, no navigation. A number that MOVES means the")
        print("    editor arrives late and every reader in this package has")
        print("    been asking too early.")
        await page.wait_for_timeout(LATE_HYDRATION_WAIT_MS)
        _show("main frame:", await _census(page))
        print(f"    frames now: {len(list(page.frames))}")

        print("\n=== HOW TO READ THIS")
        print("    textarea or input non-zero -> the editor was never")
        print("      contenteditable and no reader looked for it. Cheapest")
        print("      explanation, and the one to check first.")
        print("    a frame non-zero -> locators only search their own frame,")
        print("      so every main-frame reading was blind by construction.")
        print("    reading two differs -> late hydration; the settle is short.")
        print("    ALL zero, both readings, every frame -> the editor is in a")
        print("      CLOSED shadow root or is not in the DOM at all. Playwright")
        print("      already pierces OPEN roots, so that case is ruled out by")
        print("      the main-frame zero rather than left hanging.")
        print("    ALL elements near zero -> the page did not render and every")
        print("      other number above is meaningless. Check this first.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    asyncio.run(main())
