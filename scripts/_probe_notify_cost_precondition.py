"""Is the notifications cost measurable TODAY? Read the BEFORE half only.

WHAT THIS PROBE DELIBERATELY DOES NOT DO. It does not open the notifications
page. That is the surface whose cost is in question, opening it CLEARS the
operator's unread badge, and this wave was briefed to design and gate rather
than to fire. So this takes the BEFORE half of a before/after pair and stops.

WHY THE BEFORE HALF ALONE IS WORTH A PAGE LOAD. The blocker
``NOTIFY-COST-UNMEASURED`` reads as though somebody simply has not run the
experiment. The actual constraint is a PRECONDITION on the account, and it is
invisible until read: a badge sitting at zero makes the experiment impossible,
because a ``0 -> 0`` pair cannot distinguish "the page consumed nothing" from
"there was nothing to consume". This repository already wrote that argument
down for the sibling badge at ``shape.invitation_badge``. This probe answers
whether today is a day the experiment could say anything at all.

WHAT IT PRINTS, and the omissions are the design. COUNTS AND STATES ONLY. No
address, no aria-label, no page text of any kind. The nav label is page text
and the shaped label is still page text, so neither is printed even though
both are held in memory -- the two standing guards in this repo
(``test_navigation_is_never_derived``, ``test_page_text_is_never_printed``)
are structural and cannot know that a nav label is harmless, which is correct.
What reaches this transcript is a RELATION: how many controls were drawn, how
many carried a count, and which of three states the precondition is in.

IT CLOSES THE PAGE IT OPENS, in a ``finally``, and closes the PAGE and never
the CONTEXT -- the context is the operator's own signed-in browser session.
This matters beyond tidiness: ``BROWSER.session()`` reuses one page per
process and never closes it, and a dozen waves doing that accumulated 120 CDP
targets today, which took the attach handshake past its 15s ceiling and became
a fleet-wide outage. A wave that closes its own page is the actual fix; the
raised timeout is only a buffer.

RUN:
    LINKEDIN_CDP_ATTACH_TIMEOUT_MS=120000 LINKEDIN_CDP_ATTACH=1 \
    LINKEDIN_CDP_PORT=9224 ./venv/Scripts/python.exe \
    scripts/_probe_notify_cost_precondition.py
"""

from __future__ import annotations

import asyncio
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from linkedin_server import notify_cost  # noqa: E402
from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.auth import assert_not_authwall  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: The feed. An address on the read allowlist that this server loads for other
#: reasons anyway, chosen because the nav renders on every signed-in page and
#: this probe needs a nav and nothing else.
FEED_URL = "https://www.linkedin.com/feed/"


#: WHY THERE IS NO `_relation` HELPER HERE, and the first version had one.
#:
#: Two shipped guards refused it and both were right:
#:
#:   test_a_sanitiser_earns_its_entry::test_every_claimant_of_a_sanitiser_name_is_enrolled
#:   test_navigation_is_never_derived::test_every_relation_definition_is_byte_identical
#:
#: `_relation` is a name on the `_SANITISERS` list, so defining a function
#: with that name means **the taint guard trusts it BY NAME** -- and this one
#: had never been measured against the adversarial table that entry was earned
#: with. `_redact` was once admitted to that list on the strength of its name
#: and carried no slug rule at all, which is precisely why the enrolment half
#: exists.
#:
#: THE REMEDY IS THE STRUCTURE, NOT A DECLARATION. Enrolling would have
#: widened what the guard tolerates for a probe that does not need the url at
#: all: what is wanted is "did we land on the signed-in feed", which is a
#: QUESTION AN ASSERTION ANSWERS. So the navigation result is handed to the
#: shipped `auth.assert_not_authwall`, which RAISES, and no navigation-derived
#: value is ever bound to a name that reaches a print. Nothing to sanitise
#: means nothing to trust.


async def main() -> int:
    print("=" * 72)
    print("NOTIFY COST -- the BEFORE half, and whether today can answer at all")
    print("=" * 72)

    page = None
    try:
        async with BROWSER.session() as page:
            print("\n1. navigation")
            # RAISES rather than returns, so the url is consumed by an
            # assertion and never by a print. If it does not raise, the
            # signed-in feed was served -- which is the only fact the reading
            # below depends on, and it is now a CONSTANT string.
            assert_not_authwall(
                await BROWSER.goto(page, FEED_URL), surface="feed"
            )
            print("   relation: served-the-requested-surface")

            # ------------------------------------------------------------------
            # CONTROL FIRST. A reader that cannot see the badge it was built
            # for and a reader that sees a badge at zero are indistinguishable
            # from the outside, and this probe's entire output is a claim
            # about which of those two happened. So the two SHIPPED sibling
            # readers run on the same page: if they also read nothing, the
            # instrument is blind and no zero from this probe means anything.
            # ------------------------------------------------------------------
            print("\n2. control -- the two SHIPPED badge readers, same page")
            inv_reading = await dom.read_invitation_badge(page)
            inv = shape.invitation_badge(inv_reading)
            print("   invitation badge : state=%-11s links=%-3r counted=%r"
                  % (inv["state"], inv_reading["links"],
                     inv_reading["badge_links"]))
            # NOTE the asymmetry, because it cost this probe a run:
            # ``shape.invitation_badge`` takes the READING dict, while
            # ``shape.messaging_badge`` takes raw HTML. Two shapers over two
            # sibling badges with two different input contracts. So the
            # messaging control is reported from its reader's own output and
            # is not put through a shaper at all -- what is wanted here is
            # only "did this reader resolve", which the reading answers.
            msg_reading = await dom.read_messaging_badge(page)
            msg_resolved = bool(msg_reading.get("label"))
            print("   messaging badge  : resolved=%-5r links=%r"
                  % (msg_resolved, msg_reading.get("links")))
            controls_alive = inv["state"] == "read" or msg_resolved
            print("   at least one shipped reader resolved: %s" % controls_alive)

            # ------------------------------------------------------------------
            # 3. THE NEW READER.
            # ------------------------------------------------------------------
            print("\n3. the notifications badge -- the reader this wave added")
            reading = await notify_cost.read_notifications_badge(page)
            print("   notifications links drawn : %r" % reading["links"])
            print("   of those, carrying a count: %r" % reading["badge_links"])
            print("   read error                : %r" % reading["error"])

            verdict = notify_cost.measurability(reading)
            print("\n4. the precondition")
            print("   state      : %s" % verdict["state"])
            print("   measurable : %r" % verdict["measurable"])
            print("   unread now : %r" % verdict["unread_before"])
            print("   reversible : %r" % verdict["reversible"])
            print("   why        : %s" % verdict["why"])

            print("\n5. what this does and does not settle")
            if not controls_alive and verdict["state"] != "measurable":
                print("   NOTHING. Neither shipped reader resolved either, so")
                print("   this is a reading about the instrument or the page,")
                print("   not about the account. Do not record a zero.")
                return 3
            if verdict["state"] == "unreadable":
                print("   The BEFORE half is missing while the shipped")
                print("   controls DID resolve -- so the aim is wrong for")
                print("   this badge specifically. That is a repair on this")
                print("   module, not a fact about the cost.")
                return 4
            if verdict["state"] == "not_today":
                print("   The cost is NOT measurable on this account today.")
                print("   This is REVERSIBLE -- one arriving notification")
                print("   makes it measurable. It is not a finding about")
                print("   LinkedIn and must not retire the row as closed.")
                return 0
            print("   The cost IS measurable today. The pair would carry a")
            print("   real answer. TAKING it spends the operator's unread")
            print("   state, which is his call and not this probe's --")
            print("   nothing further was done.")
            return 0
    finally:
        # THE PAGE, NEVER THE CONTEXT. Closing the context would close his
        # signed-in browser. Guarded because a failed attach never bound one.
        if page is not None:
            try:
                await page.close()
                print("\n   [page closed]")
            except Exception as exc:  # noqa: BLE001
                print("\n   [page close failed: %s]" % type(exc).__name__)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
