"""Can a reply be composed in a conversation that already exists?

THE QUESTION, AND WHY IT OUTRANKS THE ONE BEFORE IT. Addressing a NEW message
is the hard problem: by NAME is a measured dead end -- eleven distinct needle
offsets across ten rows, accessible names 49 to 178 characters -- and by
IDENTIFIER needs an id this server can only harvest from a page that happens to
be showing one, which the viewer list supplies for two rows out of four named.

**A REPLY NEEDS NO ADDRESS AT ALL.** The conversation exists, the recipient is
already in it, and the entire recipient-gate apparatus has nothing to decide.
The capability census called replying the most job-hunt-relevant messaging
action in all 761 rows, and the economics agree: answering an InMail he was
already sent is FREE where sending one spends a finite credit whose size this
server has never been able to read.

## The two costs this is careful about, and neither is hypothetical

**THE BADGE MUST READ ZERO FIRST.** Loading messaging opens a conversation
LinkedIn chooses, and opening an UNREAD one marks a real person's message read
-- a durable record spent by somebody who is not him. That is the operator's
own standing precondition for this surface and this probe refuses without it,
rather than treating it as advice. With no unread message there is nothing to
spend.

**ONE NAVIGATION, TO A MODULE CONSTANT.** ``config.MESSAGING_URL``, and
nothing derived from it. LinkedIn redirects that address into a conversation of
its own choosing, and this reads whatever it landed on -- it never takes the
landed url and asks for it again.
``tests/test_navigation_is_never_derived.py`` scans this file like any other,
and that rule exists because handing a landed url back to the read boundary is
what put the operator's vanity slug in a traceback.

## What it prints, and why the restraint is sharper here than anywhere

COUNTS AND BOOLEANS. Nothing else.

A conversation page is a third party's words, in full, sent to him privately.
It is the richest surface in this package by a distance -- richer than the
profile payload, because a payload is markup and this is correspondence. So the
reader it calls has no field that could carry a message, a name, or a thread
id, and this script has no output path and prints no url.

**THE ONE READING THAT WOULD REFUTE THE APPROACH IS PRINTED FIRST.** If a
recipient combobox appears on a thread page, this is not the surface it looks
like and a reply is not addressless after all. Zero is expected; a non-zero is
the finding.

Run:  python scripts/_probe_thread_reply_surface.py
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


async def main() -> None:
    print("=== THE THREAD REPLY SURFACE, LIVE")
    print("    one navigation, nothing pressed, counts only\n")

    await BROWSER.start()
    async with BROWSER.session() as page:
        # --- THE PRECONDITION, AND IT IS A GATE RATHER THAN A NOTE ----------
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
            print("    REFUSED: the badge could not be read, so this cannot")
            print("    know whether opening messaging would mark somebody's")
            print("    message read. That is not the same as a zero.")
            await BROWSER.stop()
            return
        if badge.get("new_since_last_visit"):
            print("    REFUSED: there are UNREAD messages. Opening messaging")
            print("    would mark a real person's message read -- a durable")
            print("    record spent by somebody who is not him. The operator's")
            print("    standing precondition for this surface is a zero badge.")
            await BROWSER.stop()
            return

        # --- ONE NAVIGATION, TO A CONSTANT ---------------------------------
        thread_landed = await BROWSER.goto(page, MESSAGING_URL)
        # A COMPARISON, WHICH YIELDS A BOOLEAN. The landed url itself is never
        # printed and never navigated to.
        print(f"    landed inside a conversation: {'/messaging/thread/' in thread_landed}")

        reading = await dom.read_thread_reply_surface(page)
        if reading["error"]:
            print(f"    REFUSED: the surface could not be read ({reading['error']}).")
            await BROWSER.stop()
            return

        print()
        print("    THE READING THAT WOULD REFUTE THE APPROACH, FIRST:")
        print(f"      recipient comboboxes: {reading['recipient_boxes']}")
        print("      (expected ZERO -- a thread has nobody to choose. A")
        print("       non-zero here means a reply is not addressless and this")
        print("       whole route needs rethinking.)")
        print()
        print("    THE REPLY BOX:")
        print(f"      contenteditable nodes:  {reading['editors']}")
        print(f"      div[role=textbox]:      {reading['textboxes']}")
        print()
        print("    THE SUBMIT, AND ITS GATE SIGNAL:")
        print(f"      controls named Send:    {reading['send_controls']}")
        print(f"      that one is disabled:   {reading['send_disabled']!r}")
        print("      (None means NOT ASKED -- asked only when exactly one")
        print("       control matched, because asking a control that is not")
        print("       unique reads whichever one resolved first.)")

        print()
        print("=== WHAT THIS SETTLES AND WHAT IT DOES NOT")
        print("    It says whether a reply box and a submit exist on an open")
        print("    conversation, and whether the submit carries the same")
        print("    disabled-when-empty transition every other gate in this")
        print("    package rests on. That is the precondition for a reply")
        print("    capability.")
        print("    It does NOT make anything performable, and it presses")
        print("    nothing. A send is a separate ruling against a fresh")
        print("    reading, and it would still need a verification surface --")
        print("    which send_message has never had.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    asyncio.run(main())
