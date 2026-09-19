"""What KINDS of entity does his LIVE feed point at? Counts and kind words only.

## THIS PROBE HAS NEVER PRODUCED A READING. READ THIS BEFORE QUOTING IT.

It was written, and it FAILED AT THE ATTACH -- there was no browser to
attach to. Measured at 2026-09-05 21:26 by the box, at the OS level rather
than from the failure text:

    port 9224                          NO LISTENER
    chrome processes running           20
    of those carrying the debug flag    0
    port 8322 (the MCP server)         LISTENING, pid 35196

So the shared CDP Chrome the whole fleet attaches to is GONE, while the
operator's own Chrome is running beside it. **The failure text was right this
time, and that is only knowable because the port was read** -- the same
message pointed at the one thing that was NOT wrong earlier the same day, when
Chrome was answering in milliseconds and the ceiling was a timeout constant.

**RESTORING IT IS AN OPERATOR GATE, NOT AN ENGINEERING TASK**, which is why
this probe was left unrun rather than made to work. Starting a Chrome on
``--remote-debugging-port=9224`` requires quitting his existing Chrome
COMPLETELY first -- the flag is silently handed to the running instance
otherwise and no port opens -- and closing the operator's own browser is not a
thing an agent may do. The documented alternative, a separate
``--user-data-dir``, is signed into nothing, so it cannot read his feed. And
LAUNCH mode is barred outright: his profile is stamped Chrome 152 and
playwright's chromium is 151, so a launch is a DOWNGRADE -- the 2026-08-25
failure that cost the signed-in session.

**WHAT IS AND IS NOT VERIFIED ABOUT THE CODE BELOW.** Verified: it parses, all
its imports resolve, and ``FEED_URL`` is ALLOWED by ``readonly.assert_read_url``
at this tree. NOT verified: every line after the attach. Its output shape, its
badge pair, its handling of the census payload and its ``finally`` have never
executed. **Every fresh instrument built in this repository has had a bug on
its first attempt**, so treat this as an unsmoked instrument, not a ready one.
Run it the moment a CDP Chrome exists, and expect to fix something.

WHAT THIS CLOSES. ``linkedin_server/feed.py`` shipped with an explicit MEASURED
VERSUS ASSERTED section, and a corpus sweep
(``scripts/_probe_feed_kinds_in_corpus.py``) closed the cheap half of it over
1353 anchors from 35 tracked captures -- **none of which is a capture of the
feed**, which that probe prints rather than leaves to be inferred. This takes
the reading on the feed itself.

WHY IT NEEDS NO NEW READER AND NO NEW MODULE. It uses the SHIPPED
``dom.read_surface_census``, which already returns ``href_shape`` -- an href
reduced to the same placeholder vocabulary ``feed.py`` derives its markers from
(``/in/<member>``, ``/company/<company>``, ...). So no reader is added, no
pinned reader inventory moves, and no page-text call appears in this file at
all. A neighbouring wave emptied the unwired-reader inventory within the hour
and adding one here would refill it; using a shipped reader avoids taking that
from them.

**AND THAT CHOICE COSTS SOMETHING, WHICH IS STATED BEFORE THE NUMBERS RATHER
THAN AFTER.** ``href_shape`` is a PLACEHOLDER, so every member collapses to one
spelling. Therefore:

    the KIND DISTRIBUTION below is real.
    the DISTINCT-AUTHOR COUNT below is DEGENERATE and means nothing --
    it can never exceed the number of kinds. It is printed anyway, and
    labelled, because a reader who saw only the kind counts might assume
    the distinct count beneath them was live.

That is the honest trade: a shaped reader cannot count people, which is the
same property that makes it safe to run at all.

WHAT IT PRINTS: integers and words drawn from ``feed.AUTHOR_KINDS`` and
``feed.REFUSALS``. No address, no aria-label, no page text, no slug. Navigation
is consumed by ``auth.assert_not_authwall``, which RAISES -- so no
navigation-derived value is bound to a name that reaches a print, and there is
no ``_relation`` helper here to be trusted by name.

THE BADGE OBLIGATION, and it is not optional in this repository: the invitation
badge is read IMMEDIATELY BEFORE and IMMEDIATELY AFTER, and the probe reports
whether it MOVED. That is how a read proves it did not consume a counter it
passed. A badge that reads the same twice does not prove the load was free --
it proves this load did not move THIS counter -- and the output says so.

IT CLOSES THE PAGE IT OPENS, in a ``finally``, and closes the PAGE and never
the CONTEXT: the context is the operator's own signed-in browser session.

RUN:
    LINKEDIN_CDP_ATTACH_TIMEOUT_MS=120000 LINKEDIN_CDP_ATTACH=1 \
    LINKEDIN_CDP_PORT=9224 ./venv/Scripts/python.exe \
    scripts/_probe_feed_kinds_live.py
"""

from __future__ import annotations

import asyncio
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from linkedin_server import dom, feed, shape  # noqa: E402
from linkedin_server.auth import assert_not_authwall  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: The feed root. ALREADY on the read allowlist -- this probe adds no pattern
#: and consults no boundary beyond the one the shipped navigation already does.
FEED_URL = "https://www.linkedin.com/feed/"


async def main() -> int:
    print("=" * 72)
    print("THE LIVE FEED -- which KINDS of entity its controls point at")
    print("=" * 72)

    page = None
    try:
        async with BROWSER.session() as page:
            print("\n1. navigation")
            assert_not_authwall(
                await BROWSER.goto(page, FEED_URL), surface="feed"
            )
            print("   relation: served-the-requested-surface")

            # --------------------------------------------------------------
            # THE BADGE, BEFORE. Read first so the AFTER half has something to
            # be compared against. A single reading proves nothing; the PAIR
            # is the instrument.
            # --------------------------------------------------------------
            before_reading = await dom.read_invitation_badge(page)
            before = shape.invitation_badge(before_reading)
            print("\n2. invitation badge BEFORE")
            print("   state=%-11s counted=%-3r pending=%r"
                  % (before["state"], before_reading["badge_links"],
                     before["pending"]))

            # --------------------------------------------------------------
            # THE CONTROL. A census that reads zero controls and a feed with
            # no entity links are indistinguishable from outside, and every
            # number below is a claim about which happened.
            # --------------------------------------------------------------
            census = await dom.read_surface_census(page)
            print("\n3. control -- did the SHIPPED census resolve anything?")
            print("   controls read : %d" % census["controls_read"])
            print("   truncated     : %s" % census["truncated"])
            print("   census alive  : %s" % (census["controls_read"] > 0))

            shapes = [
                control.get("href_shape")
                for control in census["controls"]
                if control.get("has_href")
            ]
            print("   controls with an href : %d" % len(shapes))

            # --------------------------------------------------------------
            # THE MODULE UNDER TEST, handed the shaped hrefs.
            # --------------------------------------------------------------
            tally = feed.feed_tally(shapes)
            print("\n4. feed.feed_tally over the live shaped hrefs")
            print("   rows                  : %d" % tally["rows"])
            print("   resolved to an author : %d" % tally["identified"])
            print("   distinct  (DEGENERATE -- placeholders, see docstring)"
                  " : %d" % tally["distinct_authors"])

            print("\n5. BY KIND -- words from feed.AUTHOR_KINDS")
            if not tally["by_kind"]:
                print("   (none resolved)")
            for kind in sorted(tally["by_kind"]):
                print("   %-12s : %d" % (kind, tally["by_kind"][kind]))
            unseen = sorted(set(feed.AUTHOR_KINDS) - set(tally["by_kind"]))
            print("   kinds NOT drawn on this feed : %s" % (unseen or "none"))

            print("\n6. REFUSALS -- words from feed.REFUSALS")
            for reason in feed.REFUSALS:
                print("   %-33s : %d" % (reason, tally["refused"].get(reason, 0)))

            print("\n7. THE ASSERTED CLAIM feed.py still carries")
            ambiguous = tally["refused"].get("ambiguous_multiple_entity_kinds", 0)
            print("   two-entity paths ON THE FEED : %d" % ambiguous)
            print("   NOTE: href_shape is a placeholder, so a two-entity path")
            print("   survives shaping only if BOTH markers survive. A zero")
            print("   here is therefore weaker than a zero over raw hrefs, and")
            print("   does not retire the branch.")

            # --------------------------------------------------------------
            # THE BADGE, AFTER.
            # --------------------------------------------------------------
            after_reading = await dom.read_invitation_badge(page)
            after = shape.invitation_badge(after_reading)
            print("\n8. invitation badge AFTER")
            print("   state=%-11s counted=%-3r pending=%r"
                  % (after["state"], after_reading["badge_links"],
                     after["pending"]))
            moved = (before["state"], before["pending"]) != (
                after["state"], after["pending"]
            )
            print("   MOVED : %s" % moved)
            if not moved:
                print("   -> this load did not move THIS counter. That is not")
                print("      a claim that the load was free: a badge at zero")
                print("      cannot distinguish 'consumed nothing' from")
                print("      'there was nothing to consume'.")
    finally:
        if page is not None and not page.is_closed():
            await page.close()
            print("\npage closed (the PAGE, never the CONTEXT). is_closed=%s"
                  % page.is_closed())

    print("\nNo address, slug, aria-label or page text was printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
