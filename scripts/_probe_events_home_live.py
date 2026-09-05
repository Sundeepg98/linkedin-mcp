"""Does the events root really draw an empty "Your events" card, and what does
reading it COST?

TWO QUESTIONS, AND THE SECOND IS NOT OPTIONAL. A tool that cannot measure its
own cost refuses rather than guesses -- that is why nothing in this package
loads ``/mynetwork/``. So this reads the two nav badges BEFORE and AFTER the
one page load, on pages already being visited, and reports whether either
moved.

**BE PRECISE ABOUT WHAT THAT MEASURES.** Neither badge is an EVENTS counter:
measured offline, the events root draws no badge, no counter and no unread
indicator of any kind -- ``aria-haspopup`` 0, ``role="menu"`` 0,
``role="dialog"`` 0 across 1294108 characters. The two nav badges are the only
counters within reach of this load, so they are what "did this cost anything"
can mean here, and the honest statement of the result is "the two counters
this page could plausibly spend did not move", not "this load is free".

## THE FIRST QUESTION, AND WHY IT NEEDS A LIVE READ AT ALL

The capture already answers it: three sibling cards, the first with a heading
and an EMPTY list binding, the other two full. But the capture is one document
from one moment, and a zero read once is the same string a stale page returns.
``events.read_events_home`` is a shipped reader and this is the run that decides
whether it agrees with the document it was written against -- on a live page,
twice, with a control at both ends of the session.

## THE CONTROL

``/mypreferences/d/dark-mode``, expected 20 controls, read at the START and at
the END. 20 on six readings across two days and three builds. If it does not
read about 20, nothing else in this run is a reading. Stated as a refusal.

## NO URL IS PRINTED AND NO ``_relation`` IS DEFINED HERE

The two sibling probes each carry a byte-identical ``_relation``, asserted
identical by ``test_every_relation_definition_is_byte_identical``. A third
copy would have to be byte-identical too -- **including a docstring that names
two files** -- so it would ship a standing instruction that is one file out of
date the moment it lands. This repository has already been bitten by a
corrected document that cannot name its corrector, so rather than add a stale
copy, this file publishes only what the taint guard already treats as
untainted: a COMPARISON (a boolean, whatever it compared) and a ``len``
(an integer, whatever it counted). No branch of this file can emit a path.

## ATTACH MODE ONLY

Chrome runs externally on the operator's real profile and this attaches. A
launch-mode session opens a SECOND Chrome on that profile against a browser
build one major version behind it, which is the 2026-08-25 failure that cost
the signed-in session. Asserted below, and the refusal is shown firing.

Usage::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_events_home_live.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, events, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

EVENTS_URL = f"{BASE_URL}/events/"
CONTROL_URL = f"{BASE_URL}/mypreferences/d/dark-mode"
CONTROL_EXPECTED = 20

#: The path depth of the address ASKED for. A module constant computed from a
#: module constant, so it is this repository's own value start to finish.
ASKED_DEPTH = len([seg for seg in urlsplit(EVENTS_URL).path.split("/") if seg])


async def _badges(page, when: str) -> dict:
    """Both nav badges, read on whatever page is already open. No load.

    THE BEFORE READING MUST BE TAKEN ON A PAGE THAT DRAWS THE NAV, and the
    first version of this file got that wrong in a way worth recording: it
    read BEFORE on the dark-mode preferences page, which renders NO nav at all
    (``links: 0``), and AFTER on the events root, which renders the nav with
    no count on it (``links: 1, badge_links: 0``). Both readings came back
    with ``label: None`` and the run printed "unchanged" -- **a comparison
    between two refusals, reported as a measurement of no change.**

    ``linkedin_connections`` already had the answer: take BEFORE off the
    feed's nav, which is on the read allowlist and carries the badge on every
    signed-in render. Reading a shipped tool beats inventing a sequence.
    """
    invitation = await dom.read_invitation_badge(page)
    messaging = await dom.read_messaging_badge(page)
    shaped_invitation = shape.invitation_badge(invitation)
    # NO SHAPER IS APPLIED TO THE MESSAGING READING, and the reason is that
    # ``shape.messaging_badge`` parses an HTML STRING rather than this
    # reader's dict -- two functions of near-identical name on either side of
    # the same concept, taking different arguments. Handing it the reading
    # raises, which is how this was found. Its readability is therefore
    # decided here: a nav link, and a label off it.
    messaging_state = (
        "read"
        if int(messaging.get("links") or 0) >= 1 and messaging.get("label")
        else "unreadable"
    )
    shaped_messaging = {
        "state": messaging_state,
        "count": messaging.get("label") if messaging_state == "read" else None,
    }
    print(f"    BADGES {when}:")
    print(f"        invitation  links={invitation.get('links')} "
          f"badge_links={invitation.get('badge_links')} "
          f"state={shaped_invitation.get('state')!r} "
          f"count={shaped_invitation.get('count')!r}")
    print(f"        messaging   links={messaging.get('links')} "
          f"state={shaped_messaging['state']!r} "
          f"count={shaped_messaging['count']!r}")
    return {"invitation": shaped_invitation, "messaging": shaped_messaging}


async def _control(page, when: str) -> bool:
    if not readonly.is_read_url(CONTROL_URL):
        print(f"    CONTROL {when}: REFUSED BY THE BOUNDARY. Not a reading.")
        return False
    landed = await BROWSER.goto(page, CONTROL_URL)
    # A COMPARISON YIELDS A BOOLEAN whatever it compared -- the guard's own
    # rule, and the reason an auth-wall check is writable at all.
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    if walled:
        print(f"    CONTROL {when}: AUTH WALL. Nothing here is a reading.")
        return False
    census = await dom.read_surface_census(page)
    read = int(census.get("controls_read") or 0)
    ok = abs(read - CONTROL_EXPECTED) <= 2
    print(f"    CONTROL {when}: controls_read={read} expected "
          f"{CONTROL_EXPECTED} -- {'PASS' if ok else 'FAIL'}")
    return ok


async def _read_events(page, attempt: int) -> dict:
    landed = await BROWSER.goto(page, EVENTS_URL)
    served = str(landed) == EVENTS_URL
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    landed_depth = len(
        [seg for seg in urlsplit(str(landed)).path.split("/") if seg]
    )
    print(f"\n--- EVENTS ROOT, attempt {attempt}")
    print(f"    served exactly: {served}   auth wall: {walled}   "
          f"path depth asked {ASKED_DEPTH} -> landed {landed_depth}")
    if walled:
        return {"authwall": True}

    reading = await events.read_events_home(page)
    print(f"    cards_read={reading['cards_read']}  "
          f"rows_total={reading['rows_total']}  "
          f"verdict={reading['verdict']}  "
          f"registered_events={reading['registered_events']}  "
          f"error={reading['error']}")
    for index, card in enumerate(reading["cards"]):
        print(f"        card {index}: known={card['known']!r} "
              f"rows={card['rows']} event_links={card['event_links']} "
              f"heading_shape={card['heading_shape']!r}")
    return reading


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print("    Chrome runs externally on the operator's own profile and "
              "this script attaches to it. A launch-mode session would open a "
              "SECOND Chrome on that profile, one major version behind it.")
        print(f"    Re-run with LINKEDIN_CDP_ATTACH=1 "
              f"LINKEDIN_CDP_PORT={config.CDP_PORT}")
        return 2

    if not readonly.is_read_url(EVENTS_URL):
        print("REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    print("=== THE EVENTS ROOT, LIVE. Two readings, a control at both ends,")
    print("    and the two nav counters read before and after the load.")
    print(f"    attach mode, port {config.CDP_PORT}.")

    try:
        async with BROWSER.session() as page:
            start_ok = await _control(page, "START")
            # BEFORE OFF THE FEED'S NAV, the route linkedin_connections and
            # linkedin_new_messages both already take. The preferences page
            # this file first used draws no nav, so its badge reading was a
            # refusal wearing a zero's clothes.
            if not readonly.is_read_url(FEED_URL):
                print("    FEED REFUSED BY THE BOUNDARY. No before reading.")
                return 2
            landed = await BROWSER.goto(page, FEED_URL)
            if "/login" in str(landed) or "/checkpoint" in str(landed):
                print("    AUTH WALL ON THE FEED. Nothing here is a reading.")
                return 1
            before = await _badges(page, "BEFORE (feed nav)")
            first = await _read_events(page, 1)
            # THE AFTER READING GOES BACK TO THE FEED, and it has to.
            # Measured on the run before this line existed: the events root
            # renders the nav (invitation links=1, messaging links=1) but
            # renders NEITHER COUNT on it -- badge_links 0, label None -- so
            # an after-reading taken there is an unreadable end, and comparing
            # it to a readable feed reading is comparing a number to a
            # refusal. The feed is on the allowlist and is the same page the
            # before reading came off, which makes this a controlled
            # comparison rather than two readings of two different navs.
            on_events = await _badges(page, "ON EVENTS (both counts absent)")
            await BROWSER.goto(page, FEED_URL)
            after = await _badges(page, "AFTER (back on the feed nav)")
            second = await _read_events(page, 2)
            end_ok = await _control(page, "END")
    except Exception as error:  # noqa: BLE001
        print(f"\nRUN ABORTED: {type(error).__name__}: {error}")
        return 1

    print("\n=== VERDICT")
    if not (start_ok and end_ok):
        print("  CONTROL FAILED AT ONE END. Nothing above is a reading.")
        return 1
    if first.get("authwall") or second.get("authwall"):
        print("  AUTH WALL. Nothing above is a reading.")
        return 1

    agree = (
        first["cards_read"] == second["cards_read"]
        and first["rows_total"] == second["rows_total"]
        and first["verdict"] == second["verdict"]
        and first["registered_events"] == second["registered_events"]
    )
    print(f"  TWO READINGS AGREE: {agree}")
    print(f"  verdict: {first['verdict']}   "
          f"registered_events: {first['registered_events']}")

    print("  THE EVENTS ROOT'S OWN NAV, for the record: "
          f"invitation state={on_events['invitation'].get('state')!r} "
          f"messaging state={on_events['messaging'].get('state')!r}. "
          "A page that does not draw a counter cannot be watched spending it.")
    moved = []
    unreadable = []
    for key in ("invitation", "messaging"):
        was = before[key]
        now = after[key]
        # AN UNREADABLE END IS NOT AN UNCHANGED PAIR. Comparing two refusals
        # and printing "unchanged" is the defect this branch exists to stop.
        if was.get("state") != "read" or now.get("state") != "read":
            unreadable.append(key)
            print(f"  {key} badge: before state={was.get('state')!r} "
                  f"after state={now.get('state')!r} -- NOT A COMPARISON")
            continue
        if was.get("count") != now.get("count"):
            moved.append(key)
        print(f"  {key} badge: before={was.get('count')} "
              f"after={now.get('count')} "
              f"{'MOVED' if was.get('count') != now.get('count') else 'unchanged'}")
    if unreadable:
        print(f"  COST: NOT MEASURED for {sorted(unreadable)} -- at least one")
        print("  end was unreadable, and two refusals are not a pair. This is")
        print("  reported rather than rounded to 'nothing changed'.")
    if moved:
        print(f"  COST: {len(moved)} counter(s) moved across the load: "
              f"{sorted(moved)}")
    elif not unreadable:
        print("  COST: neither of the two counters within reach moved. The")
        print("  events root draws no counter of its own, so this is the whole")
        print("  of what 'did the load cost anything' can mean at this address.")
    return 0 if agree else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
