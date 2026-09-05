"""Does he belong to any group, is he registered for any event?

THE PRECONDITION UNDER 50 CENSUS ROWS, and nothing in this repository can
answer it. ``GROUPS-SURFACE`` (32 rows) and ``EVENTS-SURFACE`` (18) both rest
on it: if he belongs to nothing, 29 of the 32 are unreachable in principle for
this account and the largest blocker in the census is a three-row one.

THREE CHEAPER ROUTES WERE MEASURED FIRST AND ALL THREE ARE DEAD -- the
allowlist (0 of 15 addresses admitted, 7 controls passing), the RENDER (a
tabbed category's rows are not in the document until the tab is pressed,
proven by a control that had to fire and did not), and the admitted-but-
redirecting Interests address. And there is no offline route:
``_probe_membership_signal_in_corpus.py`` sweeps 30 documents and 2522736
characters for six group/event needles and finds ZERO with a firing control.
So this load is the only route, which is why the operator ruled it admissible.

## WHY THIS IS A SCRIPT AND NOT THE MCP TOOL

``linkedin_surface_census`` would be the natural instrument and its wiring is
written and NOT APPLIED: ``server.py`` is being written by another wave and a
boundary-adjacent edit taken from under a live writer is the failure this tree
has been bitten by all week. This file needs none of it -- the two addresses
are on the read allowlist as of ``6b5dad5``, and ``dom.read_surface_census``
already ships. The tool wiring remains worth having; the READS should not wait
for it.

## WHAT LEAVES THIS PROCESS: INTEGERS, SHAPES AND VERDICTS

Every control goes through ``dom.read_surface_census``, which shapes each name
and href inside itself and REDACTS the name of any control pointing at a named
entity. On these two surfaces that is most of the page, by design: a group card
links to a group, so its name is redacted and only the SHAPE of its href
survives. That is exactly the number this probe wants.

**COUNTING GROUP-MARKED HREFS IS THE MEASUREMENT.** ``/groups/<group>`` and
``/events/<event>`` are placeholders this package writes, not strings LinkedIn
serves, so counting them names nobody.

## THE COST, STATED BEFORE IT IS PAID, AND HOW THIS REPORTS IT

The operator ruled `/groups/` admissible on the ground that no cheaper route
exists -- the same ground `/notifications/` and `/messaging/` were admitted on,
and the opposite of `/mynetwork/`, which was refused because `send_invitation`
reads his own profile instead. LinkedIn draws unread-post indicators on group
cards and **whether loading the LIST consumes any of them is UNMEASURED.**

So this probe measures it rather than assuming either answer, using the two
readings it already takes: it tallies controls whose SHAPE carries an unread
vocabulary word, before and after. If the tally FALLS between readings,
something was spent and this says so. If it cannot tell, it says UNKNOWN --
never "nothing was consumed", which is a claim about an instrument this server
does not have.

## THE SETTLE PROBLEM, AND THE CONTROL THAT SOLVES IT

Neither surface has a baseline -- nobody has read either page once -- so a lone
reading of either would be uninterpretable, and this project has been burned
twice by two agreeing readings of a page that had not arrived.

TWO THINGS ARE DONE ABOUT IT. Each surface is read TWICE, because a surface
earns a baseline by being read more than once and agreeing with itself. And a
CONTROL SURFACE with a known count is read in the same session:
``/mypreferences/d/dark-mode`` draws 20 controls on six readings across two
days and three builds -- the most stable surface this server reads. **If the
control does not read about 20, nothing else this run prints is a reading.**

Usage::

    venv/Scripts/python.exe scripts/_probe_groups_events_live.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: The two addresses this wave opened, plus the CONTROL. The control is not
#: decoration: it is the only thing that makes the other two readable.
GROUPS_URL = f"{BASE_URL}/groups/"
EVENTS_URL = f"{BASE_URL}/events/"
CONTROL_URL = f"{BASE_URL}/mypreferences/d/dark-mode"

#: The control's MEASURED count, from ``server.CENSUS_SETTLED_CONTROLS``.
#: Copied as a literal rather than imported so this probe does not depend on
#: ``server.py``, which is the file it exists to route around.
CONTROL_EXPECTED = 20

#: How far below a known count a reading may fall before it is called out.
#: HALF, matching the shipped floor -- both observed half-render failures came
#: in at roughly a QUARTER, while honest variation is a few per cent.
SETTLE_FLOOR = 0.5

#: The placeholders this package writes for an entity href. Counting these
#: names nobody: LinkedIn never serves either string.
GROUP_MARKER = "/groups/<group>"
EVENT_MARKER = "/events/<event>"

#: UNREAD VOCABULARY, matched against SHAPED control names. Deliberately
#: several spellings: this is a tally whose FALL between two readings is the
#: finding, so a vocabulary that misses LinkedIn's word would report a
#: reassuring zero on both readings and call it "nothing spent".
UNREAD_WORDS = ("unread", "new post", "new posts", "new activity", "new update")


def _depth(url: str) -> int:
    return len([seg for seg in urlsplit(str(url)).path.split("/") if seg])


def _relation(landed: str, asked: str) -> str:
    """Did the address serve, or did LinkedIn send us somewhere else?

    THE INTERESTS LESSON, applied. ``/in/me/details/interests/`` is on the
    allowlist and REDIRECTS to the profile, so an admitted address is not a
    served one -- and a probe that does not compare the landed url to the
    requested one cannot tell those apart.

    RETURNS A RELATION AND NEVER A URL. Every branch below yields a literal or
    an integer depth; no part of either input survives into the result. The
    depths are taken with ``len`` rather than a helper, because counting a
    thing is the discipline this package uses INSTEAD of printing it, and
    ``tests/test_navigation_is_never_derived.py`` recognises that form.

    ITS LOCALS ARE NAMED FOR THIS FUNCTION, and that is not cosmetic. The
    consent guard tracks tainted names ACROSS A WHOLE MODULE, not per scope,
    so a local called ``before`` here made every ``before`` in this file read
    as navigation-derived -- including three in the cost report, which are
    tallies of shaped control names and touch no url at all. Three of that
    guard's four findings against this file were that collision.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


def _entity_tally(controls: list, marker: str) -> int:
    return sum(1 for row in controls if marker in str(row.get("href_shape") or ""))


def _unread_tally(controls: list) -> int:
    total = 0
    for row in controls:
        text = str(row.get("shape") or "").lower()
        if any(word in text for word in UNREAD_WORDS):
            total += 1
    return total


async def _read(page, label: str, url: str) -> dict:
    """One address, fully reported. Returns the tallies for comparison."""
    print(f"\n--- {label}  {url}")

    # THE BOUNDARY IS ASKED FIRST, AND THIS IS NOT CEREMONY. If the allowlist
    # ever loses these entries this refuses here rather than raising from
    # inside a navigation, and it says which address it refused.
    if not readonly.is_read_url(url):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return {"refused": True}

    landed = await BROWSER.goto(page, url)
    # THE RELATION IS COMPUTED BEFORE THE PRINT, so no navigation-derived name
    # appears in an output expression. The guard is right to insist: a value
    # the browser chose, handed to a print, is how the operator's slug reached
    # a transcript three times.
    relation = _relation(landed, url)
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    print(f"    relation: {relation}")
    if walled:
        print("    AUTH WALL on this address. Nothing else measured.")
        return {"authwall": True}

    census = await dom.read_surface_census(page)
    controls = list(census.get("controls") or [])
    read = int(census.get("controls_read") or 0)
    counts = census.get("counts") or {}
    groups = _entity_tally(controls, GROUP_MARKER)
    events = _entity_tally(controls, EVENT_MARKER)
    unread = _unread_tally(controls)

    print(f"    controls_read={read}  truncated={bool(census.get('truncated'))}")
    print("    " + "  ".join(
        f"{key}={int(counts.get(key) or 0)}"
        for key in ("forms", "buttons", "links", "contenteditable", "dialogs")
    ))
    print(f"    group-marked hrefs : {groups}")
    print(f"    event-marked hrefs : {events}")
    print(f"    unread-word shapes : {unread}")
    return {
        "controls": read,
        "groups": groups,
        "events": events,
        "unread": unread,
    }


def _settle(label: str, first: dict, second: dict) -> None:
    """Two readings, compared. Agreement is what earns a baseline."""
    if first.get("refused") or second.get("refused"):
        print(f"  {label:<8} NOT MEASURED -- the boundary refused it")
        return
    if first.get("authwall") or second.get("authwall"):
        print(f"  {label:<8} NOT MEASURED -- auth wall")
        return
    a, b = int(first["controls"]), int(second["controls"])
    agree = "AGREE" if a == b else "DISAGREE"
    print(f"  {label:<8} controls {a} and {b} -- {agree}")
    if a != b:
        print("           NOT A BASELINE. Two readings that disagree are two "
              "readings; only agreement earns one.")


def _cost_verdict(label: str, first: dict, second: dict) -> None:
    """Was an unread indicator spent? Report it, or say UNKNOWN.

    THE OPERATOR'S RULING HAS THREE CONDITIONS AND THIS IS TWO OF THEM:
    report what was SPENT, never claim nothing was; and where it cannot be
    told, say UNKNOWN rather than no.
    """
    if first.get("refused") or first.get("authwall"):
        print(f"  {label:<8} cost UNKNOWN -- the surface was never read")
        return
    before, after = int(first["unread"]), int(second["unread"])
    if before == 0 and after == 0:
        print(f"  {label:<8} cost UNKNOWN. Zero unread-word shapes on BOTH "
              "readings, which cannot separate 'nothing was there to spend' "
              "from 'this vocabulary does not match LinkedIn's word'. It is "
              "NOT a measurement that nothing was consumed.")
        return
    if after < before:
        print(f"  {label:<8} SPENT: unread-word shapes fell {before} -> "
              f"{after} across the two loads. Something was consumed.")
        return
    if after == before:
        print(f"  {label:<8} unread-word shapes held at {before} across both "
              "loads. Consistent with nothing being consumed by the list "
              "load, and it is ONE observation, not a guarantee.")
        return
    print(f"  {label:<8} unread-word shapes ROSE {before} -> {after}. The "
          "page changed under the probe; this says nothing about cost.")


async def main() -> int:
    print("=== GROUPS AND EVENTS, LIVE. The precondition under 50 census rows.")
    print("    Every name and href goes through dom.read_surface_census.")
    print("    Integers, shapes and verdicts only.")

    page_ref = None
    try:
        async with BROWSER.session() as page:
            page_ref = page
            print("\n### CONTROL FIRST. If this is wrong, nothing else is a reading.")
            control_first = await _read(page, "CONTROL", CONTROL_URL)

            groups_first = await _read(page, "GROUPS 1", GROUPS_URL)
            events_first = await _read(page, "EVENTS 1", EVENTS_URL)
            groups_second = await _read(page, "GROUPS 2", GROUPS_URL)
            events_second = await _read(page, "EVENTS 2", EVENTS_URL)

            print("\n### CONTROL AGAIN, at the end of the session.")
            control_second = await _read(page, "CONTROL", CONTROL_URL)
    except Exception as error:  # noqa: BLE001
        # THE PROFILE LOCK IS THE EXPECTED FAILURE AND IT IS NOT A DEFECT.
        # The MCP server holds the Chrome profile; a second driver raises
        # rather than corrupting. Said plainly so nobody debugs a working
        # guard.
        name = type(error).__name__
        print(f"\nRUN ABORTED: {name}")
        if "ProfileLocked" in name:
            print("    The Chrome profile is held by another process -- the "
                  "MCP server, or another wave's probe. This is the "
                  "cross-process guard working. Retry when the browser frees.")
        else:
            print(f"    {error}")
        return 1
    # CLOSE THE TAB THIS RUN OPENED. Measured 2026-09-05: in ATTACH mode
    # ``BROWSER._page()`` calls ``ctx.new_page()`` AND CACHES IT, and
    # ``session()``'s own ``finally`` only touches an idle timer -- so the tab
    # OUTLIVES THE PROCESS. One leaked tab per probe run, in the operator's own
    # Chrome. Across the fleet: 42 scripts call ``session()`` and 5 closed
    # their page; 27 tabs and 125 CDP targets had accumulated, and
    # ``connect_over_cdp`` enumerates every target during the handshake, which
    # is what put every wave's live work on a coin flip against a 15s ceiling.
    #
    # THE PAGE, NEVER THE CONTEXT. The context is his signed-in browser
    # session; closing it closes his window.
    #
    # AND NOT IN ``browser.py``, which is a ruling for whoever owns it rather
    # than a drive-by: ``session()`` is shared by every server tool, and those
    # legitimately REUSE the cached page across calls, so a per-session close
    # there would churn tabs for a different caller. A probe is a one-shot and
    # has nothing to keep.
    #
    # In a ``finally``, because the runs that ABORT are exactly the ones that
    # were leaking.
    finally:
        if page_ref is not None and not page_ref.is_closed():
            await page_ref.close()

    print("\n=== CONTROL, AND IT DECIDES WHETHER THE REST IS READABLE")
    verdict_ok = True
    for label, reading in (("start", control_first), ("end", control_second)):
        if reading.get("refused") or reading.get("authwall"):
            print(f"  control at {label}: NOT READ")
            verdict_ok = False
            continue
        read = int(reading["controls"])
        floor = int(CONTROL_EXPECTED * SETTLE_FLOOR)
        ok = read >= floor
        verdict_ok = verdict_ok and ok
        print(f"  control at {label}: read {read}, expected about "
              f"{CONTROL_EXPECTED}, floor {floor} -- "
              f"{'PASS' if ok else 'FAIL'}")

    print("\n=== SETTLE, from two readings each")
    _settle("groups", groups_first, groups_second)
    _settle("events", events_first, events_second)

    print("\n=== THE COST, per the operator's ruling")
    _cost_verdict("groups", groups_first, groups_second)
    _cost_verdict("events", events_first, events_second)

    print("\n=== THE PRECONDITION")
    if not verdict_ok:
        print("  NOT ANSWERED. The control failed, so every count above is a "
              "reading about this run rather than about his account. That is "
              "the distinction this project has ten catalogued defects from "
              "collapsing.")
        return 1
    for label, first, second, marker in (
        ("groups", groups_first, groups_second, "group-marked"),
        ("events", events_first, events_second, "event-marked"),
    ):
        if first.get("refused") or first.get("authwall"):
            print(f"  {label}: NOT ANSWERED -- never read")
            continue
        a, b = int(first[label]), int(second[label])
        if a == 0 and b == 0:
            print(f"  {label}: ZERO {marker} hrefs on both readings, with the "
                  "control passing. That is a NEGATIVE READING rather than a "
                  "blind one.")
        elif a == b:
            print(f"  {label}: {a} {marker} hrefs on both readings. NOT yet "
                  "proof of membership -- this root draws recommendations as "
                  "well as his own, and both are entity links. A capture is "
                  "what separates them.")
        else:
            print(f"  {label}: {a} then {b} {marker} hrefs -- the readings "
                  "DISAGREE, so neither is a count of anything yet.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
