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
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL, MESSAGING_URL  # noqa: E402

#: THE ENUMERATION EMITS RELATIONS, NEVER NAMES, and that is a decision taken
#: against a MEASUREMENT rather than out of caution.
#:
#: `scripts/_probe_messaging.py` carries a redactor built for exactly this --
#: reduce a live label to its shape -- and it is tested in both directions. It
#: was the obvious thing to reuse, and reusing a sanctioned instrument beats
#: hand-rolling a second privacy boundary. So it was tried first, offline, on
#: the labels a conversation page would actually produce:
#:
#:     Conversation with <a name>      ->  redacted   (a template rule caught it)
#:     <a name>                        ->  redacted
#:     Reply to <a name>               ->  NAME SURVIVED
#:     Open <a name> profile           ->  NAME SURVIVED
#:     Send message to <a name>        ->  NAME SURVIVED
#:
#: THE MECHANISM: its name pattern matches the MAXIMAL run of letter-words and
#: then requires EVERY word in that run to be capitalised. One lowercase word
#: anywhere in the run -- "to", "profile", "sent" -- exempts the whole run,
#: name included. The two that redact do so because an explicit template rule
#: catches them, not because the name logic works. This is reported to whoever
#: owns that file; it is not fixed from here.
#:
#: A composer control on a conversation page is very plausibly "Reply to
#: <name>", so the redactor's hole sits exactly where this probe would put its
#: input. Hence: no name is emitted at all, redacted or otherwise. What is
#: emitted is a RELATION -- how long the name is, how many words, and which of
#: a CLOSED, DECLARED vocabulary appear in it. A relation cannot carry an
#: identity, which a redacted string can whenever the redactor has a hole.
_CONTROL_VOCABULARY = (
    "send", "submit", "reply", "post", "deliver", "enter",
    "attach", "photo", "image", "gif", "emoji", "sticker", "file",
    "options", "more", "close", "expand", "delete", "discard",
    "message", "write", "draft", "compose",
)


def _name_relation(name: str | None) -> str:
    """A control's accessible name reduced to a relation. Never the name.

    The vocabulary is CLOSED and declared above, so this reports membership
    rather than content: "this control's name contains the word send" is a
    fact about the vocabulary, not about the page.
    """
    text = (name or "").strip()
    if not text:
        return "no name"
    # WHOLE WORDS, NOT SUBSTRINGS. Measured while writing this: "Open <a name>
    # profile" reported `vocab=file`, because "file" sits inside "profile" --
    # no leak, but a control that opens a profile reading as an attachment
    # button is exactly the wrong pointer to hand the next step. Splitting on
    # letter runs also keeps the match unicode-safe without a boundary
    # assertion, which is the construct that matched nothing on the typeahead.
    present = set(re.findall(r"[a-z]+", text.lower()))
    hits = [word for word in _CONTROL_VOCABULARY if word in present]
    return "words=%d chars=%d vocab=%s" % (
        len(text.split()), len(text), ",".join(hits) if hits else "-"
    )


async def _relation_for(handle) -> str:
    """The relation for one control, from both name sources.

    An icon-only submit carries `aria-label` and no text; a worded one carries
    text and no label. Reading one source only would report "no name" for half
    the candidates, which is the shape of a reading that looks like a finding.
    """
    label = await handle.get_attribute("aria-label")
    if (label or "").strip():
        return "aria-label: " + _name_relation(label)
    try:
        return "text: " + _name_relation(await handle.inner_text())
    except Exception as exc:  # noqa: BLE001
        # THE TYPE ONLY. An exception MESSAGE is composed by a library nobody
        # here controls and can carry a selector or a url -- the third sink.
        return "unreadable (%s)" % type(exc).__name__


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
        # THE DENOMINATOR BEFORE ANY COUNT, because without it every number
        # below is uninterpretable rather than zero. The first live run of
        # this probe printed the counts and not this, and the zeros were
        # reported as a finding -- which is the defect the field was added to
        # close, reproduced by the script that reads the field.
        print("    DID THE PAGE ARRIVE? Read this before any count below.")
        print(f"      elements on the page: {reading['elements']}")
        print(f"      settle verdict:       {reading['settle']!r}")
        print(f"      why:                  {reading['settle_why']}")
        if reading["settle"] == "unrendered":
            print()
            print("    STOP. The page did not render. Every count below is")
            print("    UNINTERPRETABLE, not zero -- including the refutation")
            print("    reading. Nothing here is evidence about LinkedIn.")
        print()
        print("    THE READING THAT WOULD REFUTE THE APPROACH, FIRST:")
        print(f"      recipient comboboxes: {reading['recipient_boxes']}")
        print("      (expected ZERO -- a thread has nobody to choose. A")
        print("       non-zero here means a reply is not addressless and this")
        print("       whole route needs rethinking.)")
        print()
        print("    THE REPLY BOX, ACROSS EVERY MECHANISM:")
        print(f"      contenteditable, any:   {reading['editors']}")
        print(f"      contenteditable=true:   {reading['editable_true']}")
        print(f"      div[role=textbox]:      {reading['textboxes']}")
        print(f"      textarea:               {reading['textareas']}")
        print(f"      input[type=text]:       {reading['text_inputs']}")
        print()
        print("    THE SUBMIT, AND ITS GATE SIGNAL:")
        print(f"      controls named Send:    {reading['send_controls']}")
        print(f"      that one is disabled:   {reading['send_disabled']!r}")
        print("      (None means NOT ASKED -- asked only when exactly one")
        print("       control matched, because asking a control that is not")
        print("       unique reads whichever one resolved first.)")

        # --- THE SUBMIT, ENUMERATED RATHER THAN GUESSED --------------------
        #
        # `send_controls` above asks for the exact accessible name `Send` and
        # read ZERO. Three things would explain that, and AIMING AT ANOTHER
        # GUESSED NAME is the same error as aiming at `contenteditable`, one
        # layer along, which this wave has now paid for twice:
        #
        #   1. the submit is named something else
        #   2. the submit is not a `button` role
        #   3. the submit does not exist until the textarea has content
        #
        # THE THIRD IS RANKED FIRST BECAUSE IT COSTS THE MOST IF TRUE. A
        # control that only exists once there is content cannot be observed
        # without typing, and typing turns this read into a WRITE against a
        # real conversation -- a separate ruling, not a probe decision. So the
        # structural readings below are chosen to REFUTE the third candidate
        # without touching the page: a submit that exists and is merely
        # disabled is visible right now; one that does not exist is not.
        print()
        print("    THE SUBMIT, ENUMERATED (nothing typed, nothing pressed):")
        try:
            by_type = int(await page.locator('button[type="submit"]').count())
            input_submit = int(await page.locator('input[type="submit"]').count())
            disabled = int(await page.locator("button:disabled").count())
            all_buttons = int(await page.locator("button").count())
            role_buttons = int(await page.locator('[role="button"]').count())
            forms = int(await page.locator("form").count())
            print(f"      button[type=submit]:    {by_type}")
            print(f"      input[type=submit]:     {input_submit}")
            print(f"      button, any:            {all_buttons}")
            print(f"      [role=button], any:     {role_buttons}")
            print(f"      button:disabled:        {disabled}")
            print(f"      form:                   {forms}")

            if not reading["textareas"]:
                print("      no textarea, so there is no composer to scope to.")
            else:
                # WHERE CONTROLS FIRST APPEAR RELATIVE TO THE REPLY BOX. A
                # profile, not a guessed container: walking outward from the
                # textarea and counting at each level says where the composer's
                # own furniture sits without naming a class or a test id.
                box = page.locator("textarea").first
                print()
                print("      WALKING OUT FROM THE REPLY BOX:")
                first_with = 0
                for depth in range(1, 8):
                    scope = box.locator(f"xpath=ancestor::*[{depth}]")
                    if not int(await scope.count()):
                        break
                    here = int(await scope.locator("button").count())
                    here_any = int(await scope.locator("[role=button]").count())
                    print(
                        f"        ancestor {depth}: button {here}"
                        f"  [role=button] {here_any}"
                    )
                    if here and not first_with:
                        first_with = depth

                if not first_with:
                    print()
                    print("      NO BUTTON WITHIN SEVEN LEVELS OF THE REPLY BOX.")
                    print("      That is the THIRD CANDIDATE surviving, and it is")
                    print("      the expensive one: it cannot be distinguished")
                    print("      from 'renders only once there is content' without")
                    print("      typing, which is a write and needs its own ruling.")
                    print("      STOPPING HERE rather than typing to find out.")
                else:
                    print()
                    print(f"      CONTROLS AT ANCESTOR {first_with}, AS RELATIONS:")
                    print("      (names are never emitted -- see the note at the")
                    print("       top of this file for the measurement behind that)")
                    scope = box.locator(f"xpath=ancestor::*[{first_with}]")
                    controls = scope.locator("button")
                    total = int(await controls.count())
                    for index in range(min(total, 12)):
                        one = controls.nth(index)
                        kind = await one.get_attribute("type")
                        try:
                            is_off = await one.is_disabled()
                        except Exception as exc:  # noqa: BLE001
                            is_off = "unreadable (%s)" % type(exc).__name__
                        print(
                            f"        [{index}] type={kind!r} disabled={is_off!r}"
                            f"  {await _relation_for(one)}"
                        )
                    if total > 12:
                        print(f"        ... {total - 12} more, not listed")
                    print()
                    print("      THE THIRD CANDIDATE IS REFUTED: controls exist")
                    print("      beside the reply box with nothing typed. Which")
                    print("      of the first two applies is read off the rows")
                    print("      above -- `type` answers the role question, and")
                    print("      `vocab` answers the naming one.")
        except Exception as exc:  # noqa: BLE001
            # TYPE ONLY, for the same reason as `_relation_for`.
            print(f"      ENUMERATION FAILED ({type(exc).__name__}). No counts.")

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
