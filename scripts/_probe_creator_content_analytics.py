"""DOES `/analytics/creator/content/` RENDER FOR THIS ACCOUNT AT ALL?

`CONTENT-ANALYTICS-SURFACE` holds four still-GAP rows, **every one a READ**,
at an address the boundary already admits:

    M C38  View post analytics (impressions, viewer demographics)
    M C39  View analytics for your comments
    M C40  View your creator analytics
    P G6   Per-post analytics

**The cheapest decisive question is not "what does the page contain" but
"is there a page".** Creator analytics is gated on creator mode. If the
surface does not render for this account, the four rows are MEASURED-ABSENT
and bank WITHOUT a reader being written; if it does, this capture is what a
reader gets written against instead of a guess.

**THIS IS WHY IT IS A CAPTURE AND NOT A READER.** A reader written against a
DOM nobody has seen fails closed as "he has no analytics" -- the exact answer
the surface exists to produce. Look first.

## WHAT IT MAY EMIT, AND THE RULE IS TIGHTER THAN "NO NAMES"

`linkedin_who_viewed_me` already states the resolution for an analytics
surface, and this file does not get a looser one: **numbers, enumerated UI
labels, the page's own headings SHAPED, and COUNTS of regions. Nothing else.**

Specifically REFUSED here, and each for its own reason:

* **post text** -- his own content, but his posts can NAME other people
* **viewer demographics VALUES** -- job titles, employers and locations are
  third-party organisation and role data, and a demographic breakdown is a
  description of other people however aggregated
* **any href** -- LinkedIn urls carry member and entity identifiers

## THE ZERO CARRIES ITS DENOMINATOR, ALWAYS

A zero with no denominator is indistinguishable from a page that never
loaded, and this repository has paid for that confusion repeatedly -- most
recently today, when a profile "shell" was reported from one sample of an
unstable number while the same run held 236 controls. **So every count here
is reported beside what it was counted over**, and the landed address is
reported as a RELATION rather than a url.

Run::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        LINKEDIN_CDP_ATTACH_TIMEOUT_MS=60000 \\
        ./venv/Scripts/python.exe scripts/_probe_creator_content_analytics.py

Writes NOTHING. Prints to stdout. Opens ONE tab and closes it in a `finally`.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

TARGET = f"{BASE_URL}/analytics/creator/content/"

#: Structural counts only. The selector is the measurement; its matches are
#: never printed.
REGIONS = (
    ("headings_h1", "h1"),
    ("headings_h2", "h2"),
    ("tablists", '[role="tablist"]'),
    ("tabs", '[role="tab"]'),
    ("buttons", "button"),
    ("links", "a[href]"),
    ("expandable", "[aria-expanded]"),
    ("dialogs", '[role="dialog"]'),
    ("lists", "ul, ol"),
    ("tables", "table"),
    ("images", "img"),
    ("svg_charts", "svg"),
)

#: Words that cannot be absent if this really is a content-analytics surface.
#: A vocabulary probe is worthless without a control, so this file reports the
#: hits AND the denominator it searched.
EXPECTED_VOCAB = (
    "impression", "engagement", "analytics", "post", "comment",
    "follower", "reach", "audience",
)


def _landing_class(landed: str) -> str:
    """RENAMED FROM ``_relation`` 2026-09-19, and the rename is the point.

    ``_relation`` is a name in ``tests/test_navigation_is_never_derived._SANITISERS``,
    so the taint engine trusted every call to this function BY SPELLING -- and
    this is not a copy of that function. It takes ONE argument where the
    canonical takes two, and returns its own vocabulary. Nothing had measured
    it.

    **THE RENAME VOUCHES FOR NOTHING, WHICH IS WHY IT WAS AVAILABLE TO DO.**
    Enrolling the function would ASSERT it is safe -- a claim only its author
    can make. Renaming WITHDRAWS its claim to be trusted, and requires knowing
    nothing about its contract. Those are different acts and collapsing them
    is what left a known-false trust claim standing for hours.

    It IS safe in fact -- every return below is a string constant, measured off
    the AST rather than read. That measurement is its author's to turn into an
    enrolment if this name should be trusted again.
    """
    landed = str(landed or "")
    if "/login" in landed or "/checkpoint" in landed or "/authwall" in landed:
        return "AUTH-WALL"
    if landed.rstrip("/") == TARGET.rstrip("/"):
        return "target"
    if "/analytics/" in landed:
        return "REDIRECTED-WITHIN-ANALYTICS"
    if "/feed" in landed:
        return "REDIRECTED-TO-FEED"
    return "REDIRECTED-ELSEWHERE"


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        return 2

    print("=" * 70)
    print("CONTENT-ANALYTICS-SURFACE -- does it render for this account?")
    print("=" * 70)

    # THE BOUNDARY IS CHECKED BEFORE ANYTHING IS OPENED.
    admitted = readonly.is_read_url(TARGET)
    print(f"\n  readonly.is_read_url : {admitted}")
    if not admitted:
        print("  REFUSED. Nothing is loaded.")
        return 2

    page = None
    try:
        async with BROWSER.session() as opened:
            page = opened
            landed = await BROWSER.goto(page, TARGET)
            rel = _landing_class(landed)
            # THE VERDICT IS NOT PRINTED, and the reason is a measurement.
            #
            # ``_landing_class`` returns a closed alphabet of five string
            # constants, so no input survives it and printing one leaks
            # nothing. That is true IN FACT and undeclarable IN FORM: the
            # taint engine can see "returns a constant" but has no way to say
            # "closed alphabet", and it must not be asked to take the claim on
            # trust. It already did once. While this function wore the name
            # ``_relation`` the engine trusted the call BY SPELLING, and
            # because the call looked sanitised it never examined this print
            # at all.
            #
            #     A GUARD SILENCED BY A NAME DOES NOT MERELY STOP CHECKING
            #     THAT FUNCTION. IT STOPS CHECKING EVERYTHING DOWNSTREAM
            #     OF IT.
            #
            # A COMPARISON is the engine's own sanctioned shape, so the branch
            # that matters prints as a boolean. The class itself stays in the
            # control flow below, where it was always doing the work -- what
            # is lost is a transcript line, not a diagnosis.
            print(f"  landed on target     : {rel == 'target'}")
            if rel == "AUTH-WALL":
                print("\n  AUTH WALL. Nothing here is a reading. Stopping.")
                return 1
            if rel != "target":
                # NAMED BY ITS BRANCH, NOT BY ITS VALUE: the reader learns a
                # redirect happened and that it was not the auth wall, which
                # is enough to route the failure, without the verdict string
                # reaching a sink.
                print("  redirected away from the target, and not to the "
                      "auth wall.")
            try:
                await page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception as exc:  # noqa: BLE001
                print(f"  settle wait          : {type(exc).__name__}")

            # REPEATED READINGS WITHIN ONE LOAD. A single sample of a
            # hydrating page is the error this repository retracted a finding
            # over THIS MORNING: a control proves an instrument can speak, and
            # only repetition proves what it said was stable. networkidle does
            # not settle on this surface, so stability has to be measured
            # rather than waited for.
            print("\n  STABILITY -- the same structure read 4 times, 3s apart")
            series = []
            for attempt in range(4):
                snap = {}
                for name, selector in REGIONS:
                    try:
                        snap[name] = await page.locator(selector).count()
                    except Exception as exc:  # noqa: BLE001
                        snap[name] = f"ERR:{type(exc).__name__}"
                try:
                    snap["main_chars"] = len(
                        await page.locator("main").inner_text(timeout=8_000)
                    )
                except Exception:  # noqa: BLE001
                    snap["main_chars"] = -1
                series.append(snap)
                print(f"      read {attempt}: h2={snap['headings_h2']} "
                      f"buttons={snap['buttons']} links={snap['links']} "
                      f"svg={snap['svg_charts']} main_chars={snap['main_chars']}")
                if attempt < 3:
                    await page.wait_for_timeout(3_000)

            counts = series[-1]
            moved = sorted(
                k for k in series[0]
                if any(s[k] != series[0][k] for s in series[1:])
            )
            print(f"\n      CHANGED ACROSS READS: {moved or 'nothing -- stable'}")
            print("      (a page still hydrating moves here; a settled one "
                  "does not, and only the second kind can be reported)")

            body = ""
            try:
                body = await page.locator("main").inner_text(timeout=8_000)
            except Exception:  # noqa: BLE001
                try:
                    body = await page.locator("body").inner_text(timeout=8_000)
                except Exception as exc:  # noqa: BLE001
                    print(f"      body read failed: {type(exc).__name__}")

            # THE DENOMINATOR TRAVELS WITH EVERY ZERO BELOW.
            lines = shape.content_lines(body or "")
            print(f"\n  WHAT IT WAS COUNTED OVER")
            print(f"      main_chars     {len(body or '')}")
            print(f"      content_lines  {len(lines)}")

            low = (body or "").lower()
            print("\n  VOCABULARY -- hits AND the denominator")
            # COUNTS, SPELLED WITH len() RATHER THAN str.count().
            #
            # These are integers: a count of a needle THIS FILE wrote, taken over text
            # the page wrote. Nothing of the page's is printed. The page-text guard
            # still flags str.count(), because its only call carve-out is the bare name
            # ``len`` and ``.count`` is an attribute call it cannot see through.
            #
            # len(h.split(n)) - 1 IS THE SAME INTEGER -- str.count and str.split are
            # both non-overlapping -- so the measurement is unchanged and the spelling
            # is one the guard can read. ``.count`` was deliberately NOT added to the
            # engine's carve-out list: that list matches BY SPELLING, and an exemption
            # earned by a name is how a guard stops checking everything downstream.
            hits = {w: len(low.split(w)) - 1 for w in EXPECTED_VOCAB}
            for word, n in hits.items():
                print(f"      {word:12s} {n}")
            print(f"      TOTAL vocabulary hits {sum(hits.values())} over "
                  f"{len(low)} chars")

            # HEADINGS, SHAPED. The shape is the reading; the text is not.
            print("\n  HEADINGS, SHAPED (never raw -- a heading can carry a name)")
            # THE HEADING IS MATCHED, NEVER PRINTED.
            #
            # This printed shape.census_shape(raw). The page-text guard measured that
            # function and recorded what it is: a LENGTH AND CHARSET gate that returns
            # a short plain name UNCHANGED. A heading can carry a person's name, so
            # that was a leak wearing a shaper's name, and TEXT_SANITISERS is empty on
            # purpose -- no function in this package can decide whether a string is a
            # name.
            #
            # What the probe actually needs is whether the heading is ANALYTICS-shaped
            # or FEED-shaped. EXPECTED_VOCAB is a word list THIS REPOSITORY wrote, so
            # matching against it emits tokens this file owns; a heading matching none
            # of them prints "none" and its length. A name cannot survive that.
            for sel in ("h1", "h2"):
                try:
                    n = await page.locator(sel).count()
                    for i in range(min(n, 6)):
                        raw = await page.locator(sel).nth(i).inner_text(
                            timeout=3_000
                        )
                        vocab = "/".join(
                            w for w in EXPECTED_VOCAB if w in raw.lower()
                        ) or "none"
                        print(f"      {sel}[{i}] len={len(raw):3d} "
                              f"vocab={vocab}")
                except Exception as exc:  # noqa: BLE001
                    print(f"      {sel}: {type(exc).__name__}")

            # THE CONTROL THAT DECIDES IT. The headings above are FEED-shaped
            # while the vocabulary is ANALYTICS-shaped, and those conflict.
            # One surface cannot settle it; a KNOWN surface in the same
            # session can. If /feed/ produces the same signature, then this
            # address is serving the feed and there is no analytics page here.
            print("\n  CONTROL -- the SAME readings on /feed/, same session")
            feed_sig = {}
            feed_hits = None
            try:
                await BROWSER.goto(page, f"{BASE_URL}/feed/")
                try:
                    await page.wait_for_load_state("networkidle", timeout=10_000)
                except Exception:  # noqa: BLE001
                    pass
                for name, selector in REGIONS:
                    try:
                        feed_sig[name] = await page.locator(selector).count()
                    except Exception as exc:  # noqa: BLE001
                        feed_sig[name] = f"ERR:{type(exc).__name__}"
                feed_body = await page.locator("main").inner_text(timeout=8_000)
                feed_sig["main_chars"] = len(feed_body)
                print(f"      feed: h2={feed_sig['headings_h2']} "
                      f"buttons={feed_sig['buttons']} links={feed_sig['links']} "
                      f"svg={feed_sig['svg_charts']} "
                      f"main_chars={feed_sig['main_chars']}")
                n = await page.locator("h2").count()
                for i in range(min(n, 5)):
                    raw = await page.locator("h2").nth(i).inner_text(timeout=3_000)
                    vocab = "/".join(
                        w for w in EXPECTED_VOCAB if w in raw.lower()
                    ) or "none"
                    print(f"      feed h2[{i}] len={len(raw):3d} vocab={vocab}")
                feed_low = feed_body.lower()
                feed_hits = sum(len(feed_low.split(w)) - 1 for w in EXPECTED_VOCAB)
                print(f"      feed vocabulary hits {feed_hits} over "
                      f"{len(feed_low)} chars")
            except Exception as exc:  # noqa: BLE001
                print(f"      CONTROL FAILED: {type(exc).__name__} -- no "
                      "comparison is claimed")
                feed_sig = {}
                feed_hits = None

            print("\n  VERDICT")
            rendered = (
                rel == "target"
                and isinstance(counts.get("buttons"), int)
                and counts["buttons"] > 0
                and len(body or "") > 0
            )
            print(f"      address landed at target               : {rel=='target'}")
            print(f"      a document rendered                    : {rendered}")
            print(f"      analytics vocabulary present           : "
                  f"{sum(hits.values()) > 0}")
            if feed_sig:
                same = [
                    k for k, _s in REGIONS
                    if counts.get(k) == feed_sig.get(k)
                ]
                print(f"      structural fields EQUAL to the feed    : "
                      f"{len(same)} of {len(REGIONS)}")
                print("      IF THAT IS MOST OF THEM, THIS ADDRESS IS "
                      "SERVING THE FEED.")
                # THE CONTROL'S OTHER HALF, AND UNTIL 2026-09-20 IT WAS
                # PRINTED FIFTEEN LINES FROM THE NUMBER IT EXISTS TO BE
                # COMPARED AGAINST, WITH NOTHING COMPARING THEM. A reader
                # had to hold both and do the subtraction. That is the
                # reader gating, not the probe.
                #
                # NO THRESHOLD IS INVENTED HERE. The one statement this
                # comparison supports without picking a number is the
                # positive-control law: A DISCRIMINATOR THAT SCORES ITS OWN
                # NEGATIVE CONTROL AS HIGH AS ITS TARGET CANNOT
                # DISCRIMINATE. If /feed/ carries as much analytics
                # vocabulary as this address does, a vocabulary hit here is
                # not evidence of an analytics page, and the verdict says so
                # instead of leaving it to be noticed.
                if feed_hits is not None:
                    vocab_discriminates = sum(hits.values()) > feed_hits
                    print(f"      analytics vocabulary here / on the feed: "
                          f"{sum(hits.values())} / {feed_hits}")
                    if not vocab_discriminates:
                        print("      THE VOCABULARY SIGNAL DOES NOT "
                              "DISCRIMINATE: the feed scores at least as "
                              "high, so a vocabulary hit at this address is "
                              "not evidence that an analytics page rendered.")
            print("      (a zero above is only a reading because the "
                  "denominator is printed beside it)")
    finally:
        if page is not None:
            try:
                await page.close()
                print("\n    page closed.")
            except Exception as exc:  # noqa: BLE001
                print(f"\n    page close failed: {type(exc).__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
