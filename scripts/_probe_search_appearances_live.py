"""LOAD A. His own search appearances -- the reciprocal reading for a search.

WHAT THIS IS FOR. `_audit/2026-09-05-search-results-consent.md` names this the
one reading that would let 19 reads be ruled on evidence rather than on
silence. `linkedin_who_viewed_me` reads the receiving end of a PROFILE VIEW,
and that reading is what settled whether this server may load a stranger's
profile. This reads the receiving end of a SEARCH.

WHAT IT COSTS A THIRD PARTY: nothing. The address carries no member segment,
so it resolves to whoever is signed in, and the only person on the page is him.

AND IT IS NOT THE SURFACE UNDER CONSIDERATION. `/search/results/people/` is
still refused by the read boundary and this probe does not go near it. The
gate in `_audit/2026-08-30-linkedin-nine.md` forbids one load of the page under
consideration being the evidence that authorises it, which is exactly why the
reciprocal page is the one being read.

## WHAT LEAVES THIS PROCESS

`dom.read_search_appearances` and nothing else. Past the first two paragraph
pairs the label is withheld INSIDE the page; the two that cross are shaped,
tallied and run through `census_redact_rare`; the only positive publication is
an integer count of member and company links. This probe prints its return
value and adds no reading of its own.

## THE ASYMMETRY, STATED BEFORE THE READING RATHER THAN AFTER

This instrument can REFUTE the claim that a search leaves no record. It cannot
CONFIRM it.

* A NON-ZERO headline establishes that LinkedIn records result-set membership
  and reports it back to the member. That kills the claim.
* `anchors.person` non-zero establishes that the record IDENTIFIES people.
* A ZERO or a null settles NOTHING. Zero appearances is equally consistent
  with "searches do not emit", "nobody searched for him this week", "his tier
  does not surface it", and "the page deferred and this reader, which does not
  scroll, saw a shell". Three of those four are facts about the instrument or
  the week rather than about the mechanism.

That is written here so a zero cannot later be dressed up as support for
opening the rows. An instrument that returns nothing because it cannot see the
thing is not reporting a negative.

## TWO READINGS, AND THE SECOND IS NOT A RETRY

The settle-report discipline: a surface read once has no baseline, and two
agreeing readings are what makes a number worth anything. The second reading
also answers the BADGE question the census key's own comment leaves open --
whether anything on this page is spent by loading it -- by comparing the two.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import AUTHWALL_MARKERS  # noqa: E402


async def one_reading(page, label: str) -> dict:
    """Load the page once and return what the shipped reader makes of it."""
    print(f"\n--- reading {label} ---")
    try:
        landed = await BROWSER.goto(page, dom.SEARCH_APPEARANCES_URL)
    except Exception as exc:  # noqa: BLE001 -- report, never swallow
        print(f"  NAVIGATION REFUSED: {type(exc).__name__}: {exc}")
        return {"refused": f"{type(exc).__name__}: {exc}"}

    redirected = landed.rstrip("/") != dom.SEARCH_APPEARANCES_URL.rstrip("/")
    print(f"  redirected: {redirected}")
    if any(marker in landed for marker in AUTHWALL_MARKERS):
        print("  AUTHWALL -- LinkedIn interposed a challenge; nothing was read")
        return {"authwall": True, "redirected": redirected}

    try:
        reading = await dom.read_search_appearances(page)
    except Exception as exc:  # noqa: BLE001
        print(f"  READ FAILED: {type(exc).__name__}: {exc}")
        return {"read_failed": f"{type(exc).__name__}: {exc}"}

    reading["redirected"] = redirected
    print(json.dumps(reading, indent=2, sort_keys=True))
    return reading


def verdict(first: dict, second: dict) -> None:
    """What the two readings do and do not settle. Never more than they do."""
    print("\n" + "=" * 70)
    print("WHAT THIS SETTLES ABOUT THE 21-ROW QUESTION")
    print("=" * 70)

    for name, reading in (("first", first), ("second", second)):
        for key in ("refused", "authwall", "read_failed"):
            if reading.get(key):
                print(f"\n  {name} reading did not happen: {key} = "
                      f"{reading[key]}")
                print("  NOTHING IS SETTLED. This is a blind reading, not a "
                      "negative one.")
                return

    heads = [r.get("headline") for r in (first, second)]
    people = [int(r.get("anchors", {}).get("person", 0)) for r in (first, second)]
    firms = [int(r.get("anchors", {}).get("company", 0)) for r in (first, second)]

    print(f"\n  headline    : {heads[0]}  |  {heads[1]}")
    print(f"  person links: {people[0]}  |  {people[1]}")
    print(f"  company     : {firms[0]}  |  {firms[1]}")
    print(f"  main_chars  : {first['observed']['main_chars']}  |  "
          f"{second['observed']['main_chars']}")

    if heads[0] is None and heads[1] is None:
        print("\n  NO METRIC FOUND ON EITHER READING. That is ABSENT, not "
              "zero. It is consistent with the page not rendering for this "
              "reader (which does not scroll), with the surface having moved, "
              "and with LinkedIn not serving it to this account. It is NOT "
              "evidence that a search emits nothing.")
        print("  THE 21-ROW QUESTION REMAINS UNMEASURABLE FROM HIS OWN "
              "ACCOUNT BY THIS ROUTE.")
        return

    if heads[0] != heads[1]:
        print("\n  THE TWO READINGS DISAGREE, so neither is a measurement "
              "yet. A surface read twice that answers differently has no "
              "baseline; that is the whole reason this probe reads twice.")
        return

    value = (heads[0] or {}).get("value")
    if value in ("0", None):
        print("\n  ZERO APPEARANCES, drawn by LinkedIn. This is a real "
              "reading of a real number and it STILL SETTLES NOTHING about "
              "the mechanism: it cannot separate 'searches do not emit' from "
              "'nobody searched for him this week'.")
        return

    print(f"\n  NON-ZERO: LinkedIn reports {value} and reports it TO HIM. "
          "That establishes that result-set membership is RECORDED and "
          "SURFACED to the person in the set -- which is the emission "
          "question, and it kills the claim that a people-search leaves the "
          "listed people untouched.")
    if max(people) > 0:
        # CORRECTED 2026-09-05 AFTER THE LIVE RUN, and the correction is the
        # point rather than an embarrassment. This branch printed "the record
        # does not merely count, it NAMES. The emission is identifying." It
        # read 5 and said something 5 does not support.
        #
        # anchors.person counts /in/ hrefs inside main. That is a true count
        # of member links and it does NOT establish what they point at: the
        # searchers, a "people also viewed" rail, or page chrome -- HIS OWN
        # profile link is plausibly one of them. An integer answering "are
        # there member links here" was read as answering "does the record name
        # the searchers", which is a different question needing a capture.
        print(f"  AND {max(people)} MEMBER LINKS EXIST IN main. THIS DOES NOT "
              "SAY WHOSE. It is a count of /in/ hrefs, not a finding about "
              "whether the record names the searchers -- the searchers, a "
              "suggestion rail and his own nav link all produce this number. "
              "Separating them needs a capture this probe does not take.")
    else:
        print("  NO member links on either reading: this page does not name "
              "individual searchers TO HIM. That is not the same as LinkedIn "
              "not holding the identity, and must not be reported as such.")
    print("\n  RESIDUE, unchanged by any of the above: this measures searches "
          "in which HE appeared, i.e. OTHER people's searches. Whether the "
          "class of search a tool here would run feeds this same counter is "
          "not answered, and the burden sits on the addition.")


async def main() -> int:
    if os.environ.get("LINKEDIN_CDP_ATTACH") != "1":
        print("REFUSING: set LINKEDIN_CDP_ATTACH=1 and LINKEDIN_CDP_PORT. "
              "This probe must attach to the running Chrome rather than "
              "launching one -- another wave holds the profile.")
        return 2

    print(f"url  : {dom.SEARCH_APPEARANCES_URL}")
    print(f"port : {os.environ.get('LINKEDIN_CDP_PORT')}")

    async with BROWSER.session() as page:
        first = await one_reading(page, "first")
        second = await one_reading(page, "second")

    verdict(first, second)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
