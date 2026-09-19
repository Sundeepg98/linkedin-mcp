"""Can row 50's address be NAMED without spending a /messaging/ load?

THE QUESTION. `MESSAGE-REQUESTS-SURFACE` is charged `allowlist +1` and names
no address anywhere in any tracked file. The standing rule is that such a
charge is a placeholder for an unknown until somebody names the address, and
`_audit/2026-09-05-messaging-rows.md` section 2.4 measured that the messaging
page's OWN nav does not name it either -- twelve literals, two firing
controls, and nothing matching a requests spelling.

**BUT THAT READING LEFT ONE THING OPEN AND SAID SO.** Exactly one anchor
matched `/messaging/?`, and its query was never resolved, because that probe
reads no page strings at all. This asks the same question from a surface that
costs nothing on the messaging counter.

## WHY THE FEED, AND WHY THIS IS NOT A SECOND SPEND

`/feed/` is loaded by `linkedin_new_messages`, by every badge read in this
package, and by the messaging probe itself at both ends. It does NOT redirect
into a conversation and does NOT clear the messaging badge -- that is the
entire reason it is the surface both badges are read off. **A global nav is
drawn on every page**, so if LinkedIn advertises a message-requests
destination in it, the feed carries it too.

    /messaging/ loads by this script: ZERO. It never touches the address.

## WHAT IT ADDS OVER THE SIBLING: A DENOMINATOR, SO A MISS IS A NUMBER

The sibling probe reported per-literal counts. A reader that reports only
per-literal counts cannot distinguish *"LinkedIn draws no requests link"* from
*"my literals do not spell what LinkedIn draws"* -- and this repository has
paid for that distinction repeatedly: a refusal that reports only what it did
NOT match is half a measurement.

So this counts the WHOLE messaging family first, then partitions it:

    total anchors under /messaging                          the denominator
    how many of those match at least one declared literal   the accounted-for
    the difference                                          UNACCOUNTED

**A non-zero UNACCOUNTED is the finding**: it proves an address exists that
this repository cannot currently name, and it says HOW MANY. A zero says the
family is fully spelled by the literals below, and then the requests zeros
mean what they appear to mean.

Same discipline as its sibling: **no page string enters this process.** Every
reading is a locator count over a selector written in this file. The
accounted-for figure is computed with a single CSS selector list built from
those same literals, so the partition is arithmetic over counts and never over
text read back out of the page.

Run:  LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
      ./venv/Scripts/python.exe scripts/_probe_messaging_family_off_the_feed.py

Loads /feed/ once. Presses nothing. Types nothing. Sends nothing.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL  # noqa: E402

#: THE WHOLE FAMILY. This is the denominator every count below is a share of.
_FAMILY_SELECTOR = 'a[href*="/messaging"]'

#: THE SPELLINGS, DECLARED. Deliberately wider than the sibling's twelve,
#: because that probe's own conclusion was that its literals might simply not
#: spell what LinkedIn draws. Anything matching NONE of these lands in the
#: unaccounted figure, which is the reading this file exists for.
_SPELLINGS: tuple[str, ...] = (
    "/messaging/requests",
    "/messaging/request",
    "message-requests",
    "message_requests",
    "messageRequest",
    "messagerequests",
    "filter=requests",
    "filter=other",
    "filter=focused",
    "filter=unread",
    "filter=inmail",
    "filter=starred",
    "filter=connections",
    "filter=jobs",
    "filter=spam",
    "filter=archived",
    "/messaging/thread/",
    "/messaging/compose",
    "/messaging/?",
    "/messaging/",
)


async def _count(page, selector: str) -> int | None:
    """A count, or None when the reader failed. None is never printed as 0."""
    try:
        return int(await page.locator(selector).count())
    except Exception as exc:  # noqa: BLE001
        print("      reader failed: %s" % type(exc).__name__)
        return None


async def _read_badges(page) -> tuple[tuple, tuple]:
    """Both badges, REDUCED TO PRIMITIVES AT THE BOUNDARY.

    Same shape and same reason as the sibling probe: a printer handed the whole
    shaped reading can reach ``why``, ``saw`` and ``shaped_label``, the three
    fields that can carry text LinkedIn wrote. Two scalars each cannot.
    """
    html = await page.content()
    messaging = shape.messaging_badge(html)
    invitation = shape.invitation_badge(await dom.read_invitation_badge(page))
    return (
        (messaging.get("new_since_last_visit"), messaging.get("state")),
        (invitation.get("pending"), invitation.get("state")),
    )


async def _run(page) -> None:
    landed = await BROWSER.goto(page, FEED_URL)
    if "/login" in landed or "/checkpoint" in landed:
        print("    AUTH WALL. Not signed in, so nothing was measured.")
        return

    # THE BADGES, REPORTED BUT NOT GATED ON. This script never opens messaging,
    # so there is no messaging cost for a badge to certify. They are printed
    # because a run of any live probe that does not state the account's counter
    # state leaves its reader unable to compare it with anything else.
    msg_pair, inv_pair = await _read_badges(page)
    print("\n1. THE ACCOUNT'S COUNTERS (reported, not gated on)")
    print("      messaging  new_since_last_visit=%r state=%r" % msg_pair)
    print("      invitation pending=%r state=%r" % inv_pair)

    # ---------------------------------------------------------------------
    # 2. THE DENOMINATOR FIRST. Every number below is a share of this one.
    # ---------------------------------------------------------------------
    print("\n2. THE WHOLE MESSAGING FAMILY, on the feed")
    total = await _count(page, _FAMILY_SELECTOR)
    print("      anchors under /messaging            %r" % total)
    if not total:
        print("      STOP. The feed's nav draws no messaging anchor at all, so")
        print("      every zero below is a fact about THIS PAGE and not about")
        print("      LinkedIn's addresses. A denominator of zero makes the")
        print("      partition meaningless rather than clean.")
        return

    # ---------------------------------------------------------------------
    # 3. THE PARTITION.
    # ---------------------------------------------------------------------
    print("\n3. PER-SPELLING (every literal is written in this file)")
    for spelling in _SPELLINGS:
        value = await _count(page, 'a[href*="%s"]' % spelling)
        print("      %-28s %r" % (spelling, value))

    accounted_selector = ", ".join(
        'a[href*="%s"]' % spelling for spelling in _SPELLINGS
    )
    accounted = await _count(page, accounted_selector)

    print("\n4. THE READING THIS FILE EXISTS FOR")
    print("      total messaging anchors             %r" % total)
    print("      matching at least one spelling      %r" % accounted)
    if total is None or accounted is None:
        print("      UNACCOUNTED                         unreadable")
        print("      (a reader failed, so the subtraction is not available.")
        print("       That is not zero and is not reported as zero.)")
    else:
        print("      UNACCOUNTED                         %r" % (total - accounted))
        if total - accounted > 0:
            print("      A NON-ZERO IS THE FINDING: LinkedIn draws a messaging")
            print("      address none of the declared spellings match. The")
            print("      count says how many. Naming it needs an href read,")
            print("      which is a separate decision -- a nav destination is")
            print("      furniture, but a messaging href can carry a thread id,")
            print("      and this file does not make that call.")
        else:
            print("      ZERO means the family is fully spelled by the list")
            print("      above -- so the requests zeros mean what they appear")
            print("      to mean, and row 50's address is NOT advertised in the")
            print("      global nav on any page this server loads.")


async def main() -> None:
    print("=" * 72)
    print("THE MESSAGING FAMILY, READ OFF THE FEED -- zero /messaging/ loads")
    print("=" * 72)
    async with BROWSER.session() as page:
        try:
            await _run(page)
        finally:
            # THE PAGE, NEVER THE CONTEXT.
            try:
                await page.close()
                print("\n    page closed: %r" % page.is_closed())
            except Exception as exc:  # noqa: BLE001
                print("\n    page close failed: %s" % type(exc).__name__)
            print("    /messaging/ loads taken this run: 0")


if __name__ == "__main__":
    asyncio.run(main())
