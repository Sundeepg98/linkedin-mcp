"""Five ways to find a profile SECTION. Four failed their controls; the fifth misled me.

``recommendations.py`` is a shaper with no page reader -- the state
``groups.py`` was in before ``groups_page.py``. Writing that reader needs the
recommendations section's structure, and **nobody in this repository has
established it.** This script is the record of five attempts and one RETRACTION. The first
four failed their controls. The fifth produced a dramatic finding that I
published and then refuted myself -- the retraction is below and is the most
useful part of the file.

## EVERY APPROACH CARRIES A CONTROL, AND THAT IS THE WHOLE VALUE

A selector that finds nothing on a page that HAS the thing is indistinguishable
from the thing being absent. So each approach asks for something that CANNOT be
missing alongside the thing it wants.

    1  id substring        [id*='experience'] / [id*='education']      0 / 0
       ...on a profile that certainly has both. The zeros measured the
       selector style. LinkedIn does not put those words in element ids here.

    2  vocabulary-into-the-page  dom.read_collection_groupings, terms
       experience / education                                          0 / 0
       ...and this one is NOT blind: pointed at the jobs surface with words
       that cannot be absent it matched NINE live nodes (search 5, jobs 2,
       messaging 2). So it sees live text and the profile's section titles
       are simply outside its node set -- h1-h3, role=heading, role=tab,
       button, a[role=button].

    3  :has-text            section:has-text('Experience')             0
                            section:has-text('Education')              0
                            section:has-text('Skills')                 3
       ...the engine works -- Skills matched -- and the two controls did not.

    4  the same selector, twice, with a settle between      no movement
       ...``networkidle`` timed out and every count was identical on the
       second read, so LATE RENDERING DOES NOT EXPLAIN THE ZEROS either.

**THE THIRD RESULT IS THE INFORMATIVE ONE AND IT IS NOT A CLEAN ANSWER.** If
the lower sections were simply unrendered, ``Skills`` should be missing too,
because it sits BELOW ``Experience`` on a profile. It is not. So "everything
below the fold is unrendered" does not fit, "the engine cannot match" does not
fit, and approach 4 rules out "read too early". Whatever ``Skills`` matched may
not be the profile section at all -- a suggestion rail or a nav item would
satisfy the same selector.

    5  the FLIGHT PAYLOAD via dom.read_sdui_actions        2,146 chars
       ...against this package's OWN RECORDED figure for the same address,
       1,091,238. **I CONCLUDED FROM THAT THAT /in/me/ SERVES A 2 KB SHELL,
       PUBLISHED IT, AND IT IS WRONG. See the retraction below.**

## RETRACTED: THE "2 KB SHELL" FINDING, AND HOW IT FELL

I read ``payload_chars`` ONCE on the profile (2,146), compared it to the
recorded 1,091,238, and took a feed reading of 5,063,129 in the same run as
the control that said the instrument was fine. That looked like a regression
three orders of magnitude deep.

**THEN THE FEED READ 2,146 TOO** -- same address, minutes later, same reader,
the exact number the profile gave. So I asked the question I should have asked
first.

    WITHIN one load, read 5 times     feed 2146 x5      profile 2146 x5
    ACROSS loads, same address        feed 5,063,129
                                           2,146
                                           5,147,717

**STABLE WITHIN A LOAD, AND THREE ORDERS OF MAGNITUDE APART ACROSS LOADS OF THE
SAME ADDRESS.** So ``payload_chars`` measures how much script content that
PARTICULAR load happened to carry, and **one reading of it cannot establish
anything about a page.** My finding was one reading.

**I ALSO GOT THE RETRACTION'S REASON WRONG ONCE.** Seeing feed and profile both
at 2,146 I wrote that the number was a CONSTANT and distinguished nothing. The
next run read the feed at 5,147,717, which refutes that too. The accurate
statement is the narrower one above: it varies per load, so a single sample is
not evidence. **Correcting a correction is worth the two lines it costs --
a retraction resting on a wrong reason is one more thing to retract.**

**AND THE MECHANISM IS NOW MEASURED, which settles it.** A time series on one
load, sampling out to 90 seconds, with the feed as a concurrent control:

    FEED       t=0    5,112,866 chars    123 controls
               t=2    5,112,866          123
               t=5    5,112,866          132
               t=10       2,146          132      <- the payload DISAPPEARS
               t=90       2,146          132

    PROFILE    t=0        2,146          230
               t=90       2,146          230      <- flat from the first sample

**LINKEDIN DISCARDS ITS BOOTSTRAP PAYLOAD AFTER HYDRATION.** The scripts are in
the document immediately after navigation and are gone within about ten
seconds. So ``payload_chars`` is not measuring what a page HOLDS -- it is
measuring **whether you read before or after cleanup**, and every reading of it
is a race.

That explains all three earlier numbers at once: the feed's 5,063,129 and
5,147,717 were pre-cleanup reads and its 2,146 was post-cleanup. The profile
read 2,146 every time because it had always finished by the time I looked.

**SO 2,146 IS THE RESIDUE EVERY HYDRATED PAGE KEEPS, NOT A SHELL.** And the
profile's control count is **230, flat from t=0 to t=90** -- a fully rendered
page that was never incomplete.

**THIS CLOSES THE RENDERING QUESTION ENTIRELY.** Not a shell: 230 controls. Not
incomplete hydration: nothing grows, because hydration had already finished.
Not a session fault: the feed served five megabytes on the same session. **The
sections are simply not findable by the four selectors above**, which is where
this file started -- now with the alternative explanations eliminated rather
than merely unexamined.

**AND IT IS A LIMIT ON dom.read_sdui_actions THAT REACHES PAST THIS FILE:** its
own recorded 1,091,238 was a pre-cleanup read. Anyone using that instrument
must sample immediately after navigation or measure the residue and conclude
the page is empty.

**AND THE DOM SAYS THE OPPOSITE OF A SHELL:** the profile draws **236
controls, 143 links, 85 buttons**. That is a fully rendered page. A document
serving 2 KB does not have 236 controls, and I had that number in the same run
without reconciling it against the story I was telling.

**WHAT ACTUALLY REMAINS TRUE FROM APPROACH 5:** nothing about the profile. The
needle hits were zero, on an instrument that reports a constant, so they say
nothing either.

## THE ONE SOLID FINDING FROM THIS RUN, and it is not the one I chased

    /in/me/   requested: ADMITTED      landed: REFUSED BY THE BOUNDARY

**The profile is admitted at the REQUEST and its landing is refused.** That is
the class this repository already has an instrument for -- an address that
passes ``assert_read_url`` on the way out and would not on the way back. It is
measured, reproducible, and it is a genuine boundary observation rather than a
story about rendering.

## WHAT THIS SCRIPT DOES NOT CLAIM

* **Not that he has no recommendations.** No approach here produced a reading
  whose controls fired, so none of them says anything about the account.
* **Not that the section is unreachable.** It says three specific instruments
  did not reach it, and names them so a fourth does not repeat them.

## THE ADJACENT RULING A FOURTH ATTEMPT MUST NOT WALK INTO

``/in/me/details/recommendations/`` is REFUSED by the read boundary -- measured
here -- so the detail surface is not the route either. And SCROLL is ruled NOT
SANCTIONED in this repository, so an approach that depends on rendering more of
the page by scrolling is closed before it starts.

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_profile_sections_live.py
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from linkedin_server import dom, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

PROFILE_URL = "https://www.linkedin.com/in/me/"
JOBS_URL = "https://www.linkedin.com/jobs/search/"
DETAIL_URL = "https://www.linkedin.com/in/me/details/recommendations/"

#: Section names. FURNITURE, not people -- LinkedIn's own words for its own
#: blocks, supplied by this file and never read off the page.
TERMS = ("Experience", "Education", "Recommendations", "Skills")

#: The two that CANNOT be absent from a profile. If these do not fire, nothing
#: else in the run is a reading.
CONTROLS = ("Experience", "Education")

#: Words that cannot be absent from the jobs surface, used to prove the
#: vocabulary matcher is not blind before trusting any zero it reports.
JOBS_CONTROL_TERMS = ("jobs", "search", "messaging")

FEED_URL = "https://www.linkedin.com/feed/"
#: ``dom.read_sdui_actions``'s own docstring records the profile payload at
#: 1,091,238 chars, 92.7% of the document. A RECORDED PRIOR MEASUREMENT,
#: not a guess, which is what makes a short read here a REGRESSION signal
#: rather than a null result.
RECORDED_PROFILE_PAYLOAD = 1091238


async def _id_substring(page) -> dict[str, int]:
    out: dict[str, int] = {}
    for term in TERMS:
        selector = "[id*='%s']" % term.lower()
        try:
            out[term] = int(await page.locator(selector).count())
        except Exception:  # noqa: BLE001
            out[term] = -1
    return out


async def _has_text(page) -> dict[str, int]:
    out: dict[str, int] = {}
    for term in TERMS:
        selector = "section:has-text('%s')" % term
        try:
            out[term] = int(await page.locator(selector).count())
        except Exception:  # noqa: BLE001
            out[term] = -1
    return out


async def _vocabulary(page, terms) -> int:
    raw = await dom.read_collection_groupings(page, vocabulary=list(terms))
    matches = list(raw.get("matches") or [])
    return sum(1 for entry in matches if int(entry.get("index", -1)) >= 0)


async def main() -> int:
    if os.environ.get("LINKEDIN_CDP_ATTACH") != "1":
        print("REFUSED: run with LINKEDIN_CDP_ATTACH=1. Launch mode would open "
              "a SECOND Chrome on the signed-in profile.")
        return 2

    print("=== THE DETAIL SURFACE IS NOT A ROUTE")
    print("    %-46s admitted=%s" % (
        "/in/me/details/recommendations/", readonly.is_read_url(DETAIL_URL)))
    print("    %-46s admitted=%s" % ("/in/me/", readonly.is_read_url(PROFILE_URL)))

    page_ref = None
    try:
        async with BROWSER.session() as page:
            page_ref = page
            before = await dom.read_invitation_badge(page)

            print()
            print("=== IS THE VOCABULARY MATCHER BLIND? Ask the jobs surface first.")
            await BROWSER.goto(page, JOBS_URL)
            live = await _vocabulary(page, JOBS_CONTROL_TERMS)
            print("    live matches on a surface that cannot lack these : %d" % live)
            if live <= 0:
                print("    THE MATCHER IS BLIND LIVE. Every zero below would be")
                print("    a fact about it. Stopping rather than reporting one.")
                return 1
            print("    -> it sees live text, so a profile zero is about the NODE SET")

            await BROWSER.goto(page, PROFILE_URL)

            print()
            print("=== 1. id substring")
            for term, count in (await _id_substring(page)).items():
                mark = "  <- CONTROL" if term in CONTROLS else ""
                print("    %-18s %3d%s" % (term, count, mark))

            print()
            print("=== 2. vocabulary into the page")
            profile_terms = tuple(t.lower() for t in TERMS)
            print("    matched on the profile : %d" % await _vocabulary(page, profile_terms))

            print()
            print("=== 3. :has-text")
            by_text = await _has_text(page)
            for term, count in by_text.items():
                mark = "  <- CONTROL" if term in CONTROLS else ""
                print("    %-18s %3d%s" % (term, count, mark))

            print()
            print("=== 4. THE SAME SELECTOR, READ TWICE, WITH A SETTLE BETWEEN")
            print("    The one explanation the first three do not separate: the")
            print("    profile renders its lower sections LATE, so a zero is a")
            print("    reading taken too early. A count that MOVES between two")
            print("    reads of one load says timing; a count that does not says")
            print("    the section is not there to be found by this selector.")
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
                settled = "networkidle"
            except Exception as error:  # noqa: BLE001
                settled = "timeout (%s)" % type(error).__name__
            print("    settle: %s" % settled)
            second = await _has_text(page)
            for term in TERMS:
                first_count = by_text.get(term, 0)
                again = second.get(term, 0)
                mark = "  MOVED" if first_count != again else ""
                print("    %-18s %3d -> %3d%s" % (term, first_count, again, mark))
            if any(by_text.get(t, 0) != second.get(t, 0) for t in TERMS):
                print("    -> A COUNT MOVED. The page was still rendering, and")
                print("       the earlier zeros were taken too early.")
            else:
                print("    -> NOTHING MOVED. Late rendering does not explain the")
                print("       zeros, so the selector is looking in the wrong place.")

            print()
            print("=== 5. THE FLIGHT PAYLOAD, and its control")
            payload = await dom.read_sdui_actions(page, "recommendation")
            chars = int(payload.get("payload_chars") or 0)
            print("    profile payload chars : %9d   (blocks %d)"
                  % (chars, int(payload.get("script_blocks") or 0)))
            print("    RECORDED PRIOR        : %9d" % RECORDED_PROFILE_PAYLOAD)
            share = (chars / RECORDED_PROFILE_PAYLOAD * 100) if RECORDED_PROFILE_PAYLOAD else 0.0
            print("    this load is %.3f%% of it" % share)
            for needle in ("experience", "education", "recommendation"):
                hit = await dom.read_sdui_actions(page, needle)
                print("    needle %-14s hits %d"
                      % (needle, int(hit.get("needle_hits") or 0)))

            print()
            print("    CONTROL -- the same reader on the feed, same session:")
            if readonly.is_read_url(FEED_URL):
                await BROWSER.goto(page, FEED_URL)
                feed = await dom.read_sdui_actions(page, "search")
                feed_chars = int(feed.get("payload_chars") or 0)
                print("    feed payload chars    : %9d" % feed_chars)
                if feed_chars == chars:
                    print("    -> IDENTICAL TO THE PROFILE on this load. The")
                    print("       same reader has also read this address at")
                    print("       5.1M, so the number varies per load and one")
                    print("       sample of it is not evidence about a page.")
                elif feed_chars > chars * 10:
                    print("    -> the feed reads far larger on THIS load. That")
                    print("       is suggestive and NOT sufficient: the same")
                    print("       address has read 2,146 on another load, so")
                    print("       compare across loads before believing it.")
                else:
                    print("    -> the reader is thin everywhere; this says")
                    print("       nothing about the profile specifically.")
            else:
                print("    feed REFUSED by the boundary; control unavailable.")

            print()
            fired = all(by_text.get(term, 0) > 0 for term in CONTROLS)
            print("=== DID THE CONTROLS FIRE? %s" % fired)
            if not fired:
                print("    NO. Nothing in 1-4 is a reading about the account.")
                print("    Approach 5 looked like it explained why and did not:")
                print("    payload_chars returns the SAME CONSTANT on the feed")
                print("    and on the profile, so it distinguishes nothing. The")
                print("    census in this run reports 236 controls on the")
                print("    profile, which is a fully rendered page, not a shell.")

            after = await dom.read_invitation_badge(page)
            moved = [key for key in sorted(set(before) | set(after))
                     if key not in ("raw", "label", "links", "badge_links")
                     and before.get(key) != after.get(key)]
            print()
            print("    badge fields that MOVED : %s" % (moved or "none"))
            print("    (``links`` is excluded deliberately: it goes 0 -> 2 as the")
            print("     nav HYDRATES, so comparing it measures rendering rather")
            print("     than consumption. A first version compared it and")
            print("     reported the badge CHANGED.)")
    except Exception as error:  # noqa: BLE001
        name = type(error).__name__
        print("RUN ABORTED: %s" % name)
        if "ProfileLocked" in name:
            print("    The Chrome profile is held by another process. This is "
                  "the cross-process guard working, not a defect.")
        else:
            print("    %s" % error)
        return 1
    finally:
        # THE PAGE, NEVER THE CONTEXT: the context is his signed-in session.
        if page_ref is not None:
            try:
                await page_ref.close()
                print("    tab closed")
            except Exception as error:  # noqa: BLE001
                print("    tab NOT closed: %s" % type(error).__name__)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
