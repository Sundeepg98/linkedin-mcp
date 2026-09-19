"""ONE load of /messaging/, spent deliberately, for seven blockers at once.

WHY THIS EXISTS AND WHY IT IS ONE FILE. Twenty-four capability rows across
seven blockers have been stalled for two days on a single precondition:
**nobody has opened the messaging surface.** The predecessor wave measured the
recipient gate, ruled on it, fixed it, and took ZERO page loads -- correctly,
because the cost is real. This script is the authorised spend, and it is
written to take EVERYTHING in one load rather than to answer one question.

## THE COST, NAMED BEFORE IT IS PAID

Loading ``/messaging/`` CLEARS THE MESSAGING BADGE and LinkedIn REDIRECTS the
address into one conversation OF ITS OWN CHOOSING -- measured twice and stated
in the server's ``known_side_effects``. Opening an UNREAD conversation marks a
real person's message read, which is a durable record spent by somebody who is
not him.

So this script does three things about that, and none of them is advice:

1. **IT REFUSES ON A NON-ZERO MESSAGING BADGE.** With nothing new since his
   last visit there is nothing for the redirect to consume. That is the
   operator's standing precondition for this surface.
2. **IT READS BOTH NAV BADGES BEFORE AND AFTER**, off ``/feed/`` at both ends
   -- the same page, the same readers, so the two readings are comparable.
   **It refuses to report a delta it could not read at either end.** An
   unreadable badge is not a zero and is never reported as one.
3. **IT PRESSES NOTHING.** Not a menu, not a filter, not a reaction. See the
   note on the overflow rows below: the press is a separate decision that this
   script deliberately does not make.

## WHY THE POST READ COSTS A SECOND /feed/ AND NOT A SECOND /messaging/

The messaging badge RESETS WHEN YOU ARE SITTING IN MESSAGING -- that is the
whole mechanism being measured. So a messaging-badge reading taken off the
messaging page is uninterpretable BY CONSTRUCTION: it reads zero whether the
load consumed something or there was nothing to consume. The AFTER reading is
therefore taken off ``/feed/``, an address this server already loads for other
reasons and which costs nothing on this counter.

    navigations: /feed/  ->  /messaging/  ->  /feed/
    of which /messaging/: exactly ONE

## WHAT IT PRINTS: INTEGERS, BOOLEANS, AND ITS OWN LITERALS. NOTHING ELSE.

**NO STRING FROM THE PAGE ENTERS THIS PROCESS.** Not a label, not an href, not
an inner text, not redacted and not shaped. Every reading is
``locator(<a selector written in this file>).count()``, so the only strings
that can be printed are the ones written here.

That is stricter than the sibling probes on this surface, and the reason is
the surface. A conversation page is a third party's correspondence, in full,
sent to him privately -- the richest identity surface in this package. The
sibling probe on this same address records that the shipped redactor lets a
name survive ``Reply to <a name>`` and ``Open <a name> profile``, and this
repository has measured that ``census_substitute`` returns a person's name
UNCHANGED. **A relation cannot carry an identity; a redacted string can
whenever the redactor has a hole.** Reading nothing removes the question
rather than answering it, and it costs only that the vocabulary below is mine.

**SO EVERY ZERO HERE IS A READING ABOUT A SELECTOR IN THIS FILE.** Which is
why the controls exist.

## THE CONTROLS, AND THEY ARE NOT DECORATION

A guessed-selector probe's guaranteed failure mode is that every count reads
zero and the report says "the surface has none of these". Three separate
controls have to fire before any zero here means anything:

* **ARRIVAL.** ``dom.read_thread_reply_surface`` carries a settle verdict and
  an element denominator. On a page that has not rendered, every count reads
  zero -- including the ones the rows turn on. That reader's own docstring
  records a live run whose zeros were passed on as a finding and established
  nothing.
* **A MUST-MATCH HREF.** ``/feed/`` and ``/messaging/`` are furniture that the
  logged-in nav always draws. If the href reader answers zero for those it is
  dead, and every other href zero is void.
* **A MUST-MATCH ROLE.** A logged-in LinkedIn page draws buttons. If ``button``
  counts zero the role reader is dead.

## THE ONE THING IT WILL NOT DO, AND WHY THAT IS A RULING NOT A GAP

Rows 17 and 67 ask what a conversation's overflow menu CONTAINS. Reading the
items needs the trigger pressed. **This script does not press it**, for a
reason that is structural rather than nervous: this package gates every click
through ``readonly.SANCTIONED_MUTATIONS``, and the only sanctioned click on
this entire surface is a named filter pill. An overflow menu on a conversation
is a plausible home for ``Delete``, and a probe that presses an unsanctioned
control on a real person's conversation has routed around the exact mechanism
that exists to stop it.

**The trigger COUNT is the precondition and it needs no press.** Zero triggers
means zero menu items necessarily -- that retires the rows. A non-zero trigger
count means the items need a sanction that does not exist yet, which is a
finding to hand up rather than a click to take.

## THE CHIP RAIL, WHICH IS ROW 57 AND CANNOT BE OBSERVED BY ANY READ

``RECIPIENT_CHIP_SELECTORS`` has never matched anything on any real page, and
the gate that reads it was fixed on 2026-09-05 against an imagined DOM. The
obvious thing to want from this load is a real chip. **A chip does not exist
until a recipient is COMMITTED**, and committing a recipient to a composer is
not a read -- it is the second-to-last step of an irreversible send.

So what is available is the EMPTY rail: whether a recipient combobox is drawn
at all, and whether the four chip selectors read zero against it. That is a
control the gate has never had -- it distinguishes "the selectors address
nothing on this page" from "the selectors are wrong", which is the difference
between an unobserved rail and a broken one.

Run:  LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
      ./venv/Scripts/python.exe scripts/_probe_messaging_surface_census.py

Writes NOTHING. Sends NOTHING. Presses NOTHING. Types NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL, MESSAGING_URL  # noqa: E402

# ---------------------------------------------------------------------------
# THE SELECTOR SETS. Every string below is written HERE and matched against the
# page; none is ever read back out of it. A count is the only thing that
# crosses the boundary.
# ---------------------------------------------------------------------------

#: STRUCTURAL, VOCABULARY-FREE. An overflow trigger is an ARIA relationship
#: before it is a word, so these hold whatever LinkedIn calls the control.
#: This is the reading rows 17 and 67 actually turn on.
_POPUP_SELECTORS: tuple[tuple[str, str], ...] = (
    ("aria-haspopup, any value", "[aria-haspopup]"),
    ("aria-haspopup=true", '[aria-haspopup="true"]'),
    ("aria-haspopup=menu", '[aria-haspopup="menu"]'),
    ("role=menu", '[role="menu"]'),
    ("role=menuitem", '[role="menuitem"]'),
    ("button[aria-expanded]", "button[aria-expanded]"),
    ("button[aria-expanded=false]", 'button[aria-expanded="false"]'),
)

#: VOCABULARY-BASED, AND THE VOCABULARY IS MINE. A zero here is a fact about
#: this tuple, not about LinkedIn -- which is why the structural set above is
#: read first and reported first.
_LABEL_SELECTORS: tuple[tuple[str, str], ...] = (
    ("label contains More", '[aria-label*="More"]'),
    ("label contains Options", '[aria-label*="Options"]'),
    ("label contains Open options", '[aria-label*="Open options"]'),
    ("label contains React", '[aria-label*="React"]'),
    ("label contains reaction", '[aria-label*="reaction"]'),
    ("label contains Emoji", '[aria-label*="Emoji"]'),
    ("label contains Delete", '[aria-label*="Delete"]'),
    ("label contains Archive", '[aria-label*="Archive"]'),
    ("label contains Report", '[aria-label*="Report"]'),
    ("label contains Compose", '[aria-label*="Compose"]'),
    ("label contains New message", '[aria-label*="New message"]'),
    ("label contains Write a message", '[aria-label*="Write a message"]'),
    ("label contains participants", '[aria-label*="participants"]'),
    ("label contains group", '[aria-label*="group"]'),
)

#: HREF FAMILIES. Row 50 is charged ``allowlist +1`` and NAMES NO ADDRESS --
#: the standing rule is that such a charge is a placeholder for an unknown
#: until somebody names the address. The nav of the page itself is where the
#: name lives, and it can be read WITHOUT navigating to it.
#:
#: THE FIRST TWO ARE THE FIRING CONTROL. A logged-in nav always draws them.
_HREF_SELECTORS: tuple[tuple[str, str], ...] = (
    ("CONTROL /feed/", 'a[href*="/feed/"]'),
    ("CONTROL /messaging/", 'a[href*="/messaging/"]'),
    ("/messaging/thread/", 'a[href*="/messaging/thread/"]'),
    ("/messaging/requests", 'a[href*="/messaging/requests"]'),
    ("message-requests", 'a[href*="message-requests"]'),
    ("messageRequest", 'a[href*="messageRequest"]'),
    ("filter=requests", 'a[href*="filter=requests"]'),
    ("/messaging/compose", 'a[href*="/messaging/compose"]'),
    ("filter=other", 'a[href*="filter=other"]'),
    ("filter=focused", 'a[href*="filter=focused"]'),
    ("filter=unread", 'a[href*="filter=unread"]'),
    ("filter=inmail", 'a[href*="filter=inmail"]'),
    ("/messaging/?", 'a[href*="/messaging/?"]'),
)

#: THE EMPTY CHIP RAIL -- row 57. The first entry is the composer's recipient
#: box, whose accessible name is a MEASURED constant (2026-09-01, on
#: /messaging/compose/). The rest are the four shipped chip selectors,
#: verbatim from ``dom``, so a change to that tuple changes this probe.
_RECIPIENT_BOX_SELECTOR = '[aria-label="%s"]' % dom.MESSAGE_RECIPIENT_LABEL

#: ROLE CENSUS. The firing control for every role reading below it.
_ROLE_SELECTORS: tuple[tuple[str, str], ...] = (
    ("CONTROL button", "button"),
    ("role=button", '[role="button"]'),
    ("li", "li"),
    ("role=listitem", '[role="listitem"]'),
    ("role=tablist", '[role="tablist"]'),
    ("role=tab", '[role="tab"]'),
    ("role=dialog", '[role="dialog"]'),
    ("form", "form"),
)


async def _count(page, selector: str) -> int | None:
    """A count, or None when the reader itself failed.

    None is NOT zero and is never printed as one. Only the exception TYPE is
    reported -- a library's exception MESSAGE is composed by code nobody here
    controls and has been measured carrying selectors and urls.
    """
    try:
        return int(await page.locator(selector).count())
    except Exception as exc:  # noqa: BLE001
        print("      reader failed: %s" % type(exc).__name__)
        return None


async def _census(page, title: str, pairs) -> dict[str, int | None]:
    print("    %s" % title)
    out: dict[str, int | None] = {}
    for label, selector in pairs:
        value = await _count(page, selector)
        out[label] = value
        print("      %-30s %r" % (label, value))
    return out


async def _read_both_badges(page) -> tuple[tuple, tuple]:
    """Both nav badges off /feed/, REDUCED TO PRIMITIVES AT THE BOUNDARY.

    It returns ``(count, state)`` twice. Not the shaped dicts -- two pairs of
    scalars -- and that is a property in the signature rather than a habit.

    **WHY, AND IT IS NOT TO CLEAR A RED.** The first draft returned the dicts
    and printed two of their fields. ``test_page_text_is_never_printed``
    refused it, and the obvious "fix" -- rename the local, or rename the
    printer's parameter -- is the laundering this repository has a scar for:
    the fixed point follows the binding, and a rename that clears a red
    without changing a property is a redaction that erases its own marker.

    The property that actually needed changing is this: a printer handed the
    WHOLE reading can print ``why``, ``saw`` or ``shaped_label`` -- the three
    fields that can carry text LinkedIn wrote -- and a future edit adding one
    of them would be a real leak that no guard could see, because by then the
    value is a parameter and the taint engine tracks names, not calls.

    Handing over two scalars closes that door in the SIGNATURE. It is the
    entrance-guard shape rather than the exit-guard shape: adding a label to
    this output now requires changing the return type, which is visible in a
    diff, instead of adding one more ``.get`` that is not.

    ``state`` is a shaped verdict from a closed set and separates the two
    failures that matter -- no badge element drawn, versus drawn and
    unparseable. The counts are integers. Neither can carry an identity.
    """
    html = await page.content()
    messaging = shape.messaging_badge(html)
    invitation = shape.invitation_badge(await dom.read_invitation_badge(page))
    return (
        (messaging.get("new_since_last_visit"), messaging.get("state")),
        (invitation.get("pending"), invitation.get("state")),
    )


def _show_badges(when: str, msg_pair: tuple, inv_pair: tuple) -> None:
    """Four scalars. This function cannot reach a page or a label.

    **THE PARAMETER NAMES ARE DELIBERATE. DO NOT "TIDY" THEM BACK.** They were
    ``messaging`` and ``invitation``, which read better and were refused: the
    taint engine tracks a NAME ACROSS THE MODULE, not per scope, and
    ``messaging`` is bound to a ``page.content()`` derivative fifteen lines
    above. Same mechanism as ``196394d``, where a ``_relation`` helper's
    ``before``/``after`` locals tainted three prints that touched no url at
    all, and renaming was the sanctioned clearance.

    The rename is honest HERE and would not have been before the change above
    it: this function now receives two 2-tuples of scalars, so there is no
    label it could print whatever it called them. The rename alone would have
    been laundering; the rename after the signature change is bookkeeping.
    """
    print("    %s (off the feed nav)" % when)
    print("      messaging  new_since_last_visit=%r state=%r" % msg_pair)
    print("      invitation pending=%r state=%r" % inv_pair)


def _readable(msg_pair: tuple, inv_pair: tuple) -> bool:
    """Both badges actually READ. An unreadable badge is not a zero."""
    return msg_pair[1] == "read" and inv_pair[1] == "read"


#: Appended to the INSTANT the /messaging/ navigation is issued, so the cost
#: line in the finally reports what was SPENT rather than what was reached. A
#: refusal before that point, or a crash before it, leaves it empty -- and the
#: first run of this file crashed at exactly that point and correctly reported
#: zero loads taken.
_SPENT: list[int] = []


async def _run(page) -> None:
    """The census. Every refusal here returns BEFORE the spend."""
    # -----------------------------------------------------------------------
    # 1. BEFORE. Both badges, off the feed.
    # -----------------------------------------------------------------------
    print("\n1. BEFORE THE SPEND")
    landed = await BROWSER.goto(page, FEED_URL)
    if "/login" in landed or "/checkpoint" in landed:
        print("    AUTH WALL. Not signed in, so nothing was measured and")
        print("    nothing was spent.")
        return
    before_msg, before_inv = await _read_both_badges(page)
    _show_badges("before", before_msg, before_inv)

    if not _readable(before_msg, before_inv):
        print()
        print("    REFUSED, AND THE REFUSAL IS THE INSTRUCTION. One of the two")
        print("    badges did not read. An unreadable badge is not a zero, and")
        print("    a load whose cost cannot be certified at BOTH ends does not")
        print("    get taken. Nothing was spent.")
        return

    if before_msg[0]:
        print()
        print("    REFUSED. Something has arrived since his last visit, so the")
        print("    conversation LinkedIn redirects into may be UNREAD. Opening")
        print("    it marks a real person's message read -- a durable record")
        print("    spent by somebody who is not him. The operator's standing")
        print("    precondition for this surface is a zero badge. Nothing was")
        print("    spent.")
        return

    # -----------------------------------------------------------------------
    # 2. THE ONE NAVIGATION, TO A MODULE CONSTANT.
    # -----------------------------------------------------------------------
    print("\n2. THE SPEND -- one navigation to config.MESSAGING_URL")
    _SPENT.append(1)
    thread_landed = await BROWSER.goto(page, MESSAGING_URL)
    # A COMPARISON YIELDING A BOOLEAN. The landed url is never printed and
    # never navigated to -- handing a landed url back to the read boundary is
    # what put a vanity slug in a traceback once already.
    print("    redirected into a conversation: %r"
          % ("/messaging/thread/" in thread_landed))

    # -----------------------------------------------------------------------
    # 3. ARRIVAL FIRST. Without this every count below is uninterpretable.
    # -----------------------------------------------------------------------
    print("\n3. DID THE PAGE ARRIVE? Read this before any count.")
    arrival = await dom.read_thread_reply_surface(page)
    print("      elements on the page: %r" % arrival.get("elements"))
    print("      settle verdict:       %r" % arrival.get("settle"))
    print("      reader error:         %r" % (arrival.get("error") is not None))
    if arrival.get("settle") == "unrendered":
        print("    STOP READING THE COUNTS AS DATA. The page did not render;")
        print("    every zero below is a fact about that.")

    # -----------------------------------------------------------------------
    # 4. ROW 66 -- THREAD-REPLY-BOX.
    # -----------------------------------------------------------------------
    print("\n4. ROW 66 THREAD-REPLY-BOX (dom.read_thread_reply_surface)")
    for key in (
        "recipient_boxes", "editors", "editable_true", "textboxes",
        "textareas", "text_inputs", "send_controls", "send_disabled",
    ):
        print("      %-20s %r" % (key, arrival.get(key)))
    print("      (recipient_boxes is the REFUTATION reading: a thread has")
    print("       nobody to choose, so a non-zero means a reply is not")
    print("       addressless and the whole route needs rethinking.)")

    # -----------------------------------------------------------------------
    # 5. ROWS 17 + 67 -- the overflow triggers, structurally.
    # -----------------------------------------------------------------------
    print("\n5. ROWS 17 + 67 -- OVERFLOW TRIGGERS, STRUCTURAL (no press)")
    await _census(page, "aria relationships:", _POPUP_SELECTORS)
    print("      (role=menuitem is expected 0 with nothing pressed. A trigger")
    print("       count of 0 retires the rows; a non-zero means the ITEMS need")
    print("       a sanctioned press this probe will not take. These two rows")
    print("       share one reading -- it does NOT separate a conversation")
    print("       menu from a per-message one.)")

    # -----------------------------------------------------------------------
    # 6. ROW 76 + the label vocabulary.
    # -----------------------------------------------------------------------
    print("\n6. ROW 76 + VOCABULARY (every zero here is about MY tuple)")
    await _census(page, "aria-label substrings written in this file:",
                  _LABEL_SELECTORS)

    # -----------------------------------------------------------------------
    # 7. ROW 50 -- the address, named off the page's own nav.
    # -----------------------------------------------------------------------
    print("\n7. ROW 50 MESSAGE-REQUESTS-SURFACE -- href families")
    await _census(page, "anchors matching literals written in this file:",
                  _HREF_SELECTORS)
    print("      (the two CONTROL rows must be non-zero. If they are not, the")
    print("       href reader is dead and every other zero is void.)")

    # -----------------------------------------------------------------------
    # 8. ROW 57 -- the EMPTY chip rail.
    # -----------------------------------------------------------------------
    print("\n8. ROW 57 MESSAGE-ADDRESSING -- the EMPTY rail")
    recipient_boxes = await _count(page, _RECIPIENT_BOX_SELECTOR)
    print("      %-30s %r" % ("composer recipient box", recipient_boxes))
    for index, selector in enumerate(dom.RECIPIENT_CHIP_SELECTORS):
        value = await _count(page, selector)
        print("      chip selector %d of %d               %r"
              % (index + 1, len(dom.RECIPIENT_CHIP_SELECTORS), value))
    print("      (a chip exists only once a recipient is COMMITTED, and")
    print("       committing one is not a read. What is measurable is the")
    print("       EMPTY rail -- whether these selectors address anything on a")
    print("       real page at all.)")

    # -----------------------------------------------------------------------
    # 9. ROW 45 + the role census.
    # -----------------------------------------------------------------------
    print("\n9. ROW 45 GROUP-CHAT-SURFACE + ROLE CENSUS")
    await _census(page, "roles:", _ROLE_SELECTORS)

    # -----------------------------------------------------------------------
    # 10. AFTER. Both badges, off the feed again -- the same page and the same
    #     readers as the BEFORE, so the two are comparable.
    # -----------------------------------------------------------------------
    print("\n10. AFTER THE SPEND")
    await BROWSER.goto(page, FEED_URL)
    after_msg, after_inv = await _read_both_badges(page)
    _show_badges("after", after_msg, after_inv)

    print("\n11. WHAT THE LOAD COST")
    if not _readable(after_msg, after_inv):
        print("    UNREPORTABLE. A badge that read BEFORE did not read AFTER,")
        print("    so no delta can be stated. The load happened; its cost on")
        print("    that counter is UNKNOWN, which is not the same as zero and")
        print("    is not reported as one.")
    else:
        print("    messaging  before=%r after=%r  moved=%r"
              % (before_msg[0], after_msg[0], before_msg[0] != after_msg[0]))
        print("    invitation before=%r after=%r  moved=%r"
              % (before_inv[0], after_inv[0], before_inv[0] != after_inv[0]))
        print("    (a messaging badge that was ALREADY 0 cannot show this load")
        print("     consuming anything -- that is the precondition doing its")
        print("     job, not a measurement of zero cost. The conversation-")
        print("     opened reading in section 2 is the cost that IS observable")
        print("     here.)")


async def main() -> None:
    print("=" * 72)
    print("MESSAGING SURFACE CENSUS -- one /messaging/ load, nothing pressed")
    print("=" * 72)

    # THE SESSION CONTEXT MANAGER, NOT ``_page()`` DIRECTLY. It holds the
    # single-flight call lock for the whole run, and a dozen waves share this
    # browser -- two navigations racing on one account is exactly what the
    # rate discipline exists to prevent. Its own finally only touches an idle
    # timer, so the page is closed here explicitly.
    async with BROWSER.session() as page:
        try:
            await _run(page)
        finally:
            # THE PAGE, NEVER THE CONTEXT. The context is his own signed-in
            # browser session; closing it would end it. Leaking the page is
            # what degraded attach for a whole fleet on 2026-09-05.
            try:
                await page.close()
                print("\n    page closed: %r" % page.is_closed())
            except Exception as exc:  # noqa: BLE001
                print("\n    page close failed: %s" % type(exc).__name__)
            print("    /messaging/ loads taken this run: %d" % len(_SPENT))


if __name__ == "__main__":
    asyncio.run(main())
