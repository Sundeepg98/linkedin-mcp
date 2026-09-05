"""Can the section split be done with LOCATORS ONLY -- no ``page.evaluate``?

WHY THIS QUESTION IS THE WHOLE WAVE. ``scripts/_probe_membership_tally_live.py``
splits his Groups page correctly and does it with a ``page.evaluate`` call.
This package confines ``page.evaluate`` to ``dom.py`` behind an explicit
waiver, and ``dom.py`` is the module ``server.py``'s ``publish_post`` audience
refusal keys on by FEATURE DETECTION -- so putting a groups reader there means
adding a name to the one module where an unlucky name re-arms an irreversible
broadcast. ``premium.py``, ``newsletters.py`` and ``notify_cost.py`` all avoid
that by being locator-only, and each says so.

**THE ALTERNATIVE THAT LOOKS EASIER IS MEASURED WRONG.** A flat sweep of every
group anchor answers TEN where the truth is FIVE, in the flattering direction,
because the suggestion rows carry group anchors too. So "locator-only" is not
allowed to mean "give up on the split".

## THE RULE, COPIED FROM THE VALIDATED DIRECTION AND NOT RE-DERIVED

    Start at the CONTROL, never at the anchor. Climb parents. The first
    ancestor holding at least one group anchor is the stopping ancestor; the
    control QUALIFIES only if that ancestor holds EXACTLY ONE. That one anchor
    is a MEMBERSHIP. Every other group anchor is a suggestion or the root.

A containment rule is not symmetric -- the identical rule run from the ANCHOR
resolved zero rows against five on the same page in the same hour. That is
already written up; this probe inherits the direction rather than re-testing
it.

## WHAT IS ACTUALLY BEING TESTED HERE

Whether Playwright's ``locator.locator("xpath=..")`` chain can express that
climb. If it can, the reader needs no waiver and lands in a module of its own.
If it cannot, the honest answer is that the reader belongs in ``dom.py`` and
that is a ruling somebody has to make loudly.

**THE CONTROL IT MUST PASS: exactly FIVE membership rows and FIVE others with
ZERO identifiers in common.** Four independent instruments agree on five. A
reading of TEN is this repository's known defect arriving again, not a new
fact, and this probe REFUSES to publish rather than reporting it as a result.

## COST

The groups page's nav carries no count-bearing mynetwork link, so the
invitation badge is read on the FEED at both ends -- the page that carries the
instrument. That is one extra navigation and it buys a reading that can move.
The badge is known to sit at zero on this account, so an UNMOVED zero is
recorded as DEGENERATE rather than as proof of no cost.

Usage::

    LINKEDIN_CDP_ATTACH_TIMEOUT_MS=120000 LINKEDIN_CDP_ATTACH=1 \\
        LINKEDIN_CDP_PORT=9224 venv/Scripts/python.exe \\
        scripts/_probe_groups_locator_walk.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, groups, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

GROUPS_URL = f"{BASE_URL}/groups/"
CONTROL_URL = f"{BASE_URL}/mypreferences/d/dark-mode"
CONTROL_EXPECTED = 20

#: The anchor aim. A CSS attribute-substring match, which is looser than the
#: pathname rule the evaluate-based probe used -- a href carrying the segment
#: in a QUERY would match here and not there. That is deliberate and safe in
#: this direction: the loose aim only decides which elements are CANDIDATES,
#: and ``groups.group_identifier`` re-parses every survivor with ``urlsplit``
#: and refuses anything whose PATH does not carry the segment. The loose half
#: can over-collect; it cannot publish.
ANCHOR = 'a[href*="/groups/"]'
CONTROL = "button[aria-expanded]"

#: How far up to climb before giving up on a control. Bounded because an
#: unbounded climb on an unfamiliar page is a cost nobody chose; 40 is deeper
#: than any row wrapper measured on this surface and the probe REPORTS any
#: control that exhausts it rather than silently dropping it.
MAX_CLIMB = 40


async def _stopping_ancestor(control):
    """The first ancestor of ``control`` holding at least one group anchor.

    Returns ``(locator, anchors_found, depth)`` or ``(None, 0, depth)`` if the
    climb exhausted ``MAX_CLIMB``.

    LOCATORS ONLY. ``xpath=..`` is Playwright's documented parent step and is
    the whole mechanism -- no script is evaluated in the page.
    """
    node = control
    for depth in range(1, MAX_CLIMB + 1):
        node = node.locator("xpath=..")
        try:
            found = int(await node.locator(ANCHOR).count())
        except Exception:  # noqa: BLE001 - climbed off the top of the document
            return None, 0, depth
        if found >= 1:
            return node, found, depth
    return None, 0, MAX_CLIMB


async def split_locator_only(page) -> dict:
    """The section split, with no ``page.evaluate`` anywhere.

    Raw hrefs live in this function and in ``groups.membership_tally``. They
    are not printed, not logged and not interpolated into any message.
    """
    anchors = page.locator(ANCHOR)
    total = int(await anchors.count())
    all_hrefs: list[str] = []
    for index in range(total):
        all_hrefs.append(
            str(await anchors.nth(index).get_attribute("href") or "")
        )

    controls = page.locator(CONTROL)
    control_count = int(await controls.count())

    with_control: list[str] = []
    rows_found = 0
    rows_not_scoped = 0
    climbs_exhausted = 0
    stopping_widths: dict[int, int] = {}

    for index in range(control_count):
        row, found, _depth = await _stopping_ancestor(controls.nth(index))
        if row is None:
            climbs_exhausted += 1
            continue
        stopping_widths[found] = stopping_widths.get(found, 0) + 1
        if found != 1:
            rows_not_scoped += 1
            continue
        rows_found += 1
        with_control.append(
            str(await row.locator(ANCHOR).first.get_attribute("href") or "")
        )

    # WITHOUT = every anchor MINUS one occurrence per claimed href. A count
    # subtraction rather than a set difference, so a page drawing the same
    # group twice loses one copy rather than both.
    remaining = list(all_hrefs)
    rows_sharing_an_anchor = 0
    claimed: list[str] = []
    for href in with_control:
        if href in remaining:
            remaining.remove(href)
            claimed.append(href)
        else:
            # Two controls resolved to the same anchor href and the anchor
            # list has no third copy. Reported, never silently merged.
            rows_sharing_an_anchor += 1

    return {
        "anchors": total,
        "controls": control_count,
        "rows_found": rows_found,
        "rows_not_row_scoped": rows_not_scoped,
        "climbs_exhausted": climbs_exhausted,
        "rows_sharing_an_anchor": rows_sharing_an_anchor,
        "stopping_widths": stopping_widths,
        "with_control": claimed,
        "without_control": remaining,
    }


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set. A launch-mode session "
              "would open a SECOND Chrome on the operator's own profile.")
        return 2
    if not readonly.is_read_url(GROUPS_URL):
        print("REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    print("=== LOCATOR-ONLY SECTION SPLIT -- can the walk be done without a "
          "page.evaluate waiver?")

    page_ref = None
    verdict_rows = None
    overlap = None
    control_before = control_after = 0
    try:
        async with BROWSER.session() as page:
            page_ref = page
            await BROWSER.goto(page, CONTROL_URL)
            control_before = int(
                (await dom.read_surface_census(page)).get("controls_read") or 0
            )
            await BROWSER.goto(page, FEED_URL)
            badge_before = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            print(f"    control census BEFORE: {control_before} "
                  f"(expect about {CONTROL_EXPECTED})")
            print(f"    feed invitation badge BEFORE: "
                  f"{badge_before.get('state')} {badge_before.get('pending')}")

            landed = await BROWSER.goto(page, GROUPS_URL)
            if "/login" in str(landed) or "/checkpoint" in str(landed):
                print("    AUTH WALL. Nothing measured.")
                return 1
            print("    served the address asked for: "
                  f"{str(landed).rstrip('/') == GROUPS_URL.rstrip('/')}")

            split = await split_locator_only(page)

            try:
                membership = groups.membership_tally(split["with_control"])
                suggestion = groups.membership_tally(split["without_control"])
                overlap = groups.disjoint(
                    split["with_control"], split["without_control"]
                )
            except Exception as error:  # noqa: BLE001
                print(f"    THE REDUCER RAISED: {type(error).__name__}. "
                      "Message withheld -- this scope holds raw hrefs.")
                return 1
            verdict_rows = membership

            print(f"\n=== ANCHORS {split['anchors']}, CONTROLS "
                  f"{split['controls']}")
            print(f"    row-scoped (stopping ancestor held exactly 1): "
                  f"{split['rows_found']}")
            print(f"    NOT row-scoped: {split['rows_not_row_scoped']}, "
                  f"climbs exhausted: {split['climbs_exhausted']}, "
                  f"shared an anchor: {split['rows_sharing_an_anchor']}")
            print(f"    stopping-ancestor widths: {split['stopping_widths']}")
            for label, tally in (
                ("MEMBERSHIPS (row-scoped control)", membership),
                ("EVERYTHING ELSE (suggestions + root)", suggestion),
            ):
                print(f"    {label}: rows {tally['rows']}, groups "
                      f"{tally['groups']}, DISTINCT {tally['distinct']}, "
                      f"refused {tally['refused'] or 'none'}")
            print(f"    in common {overlap['in_common']}, DISJOINT "
                  f"{overlap['disjoint']}")

            badge_on_groups = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            print(f"\n    invitation badge ON THE GROUPS PAGE: "
                  f"{badge_on_groups.get('state')}")
            await BROWSER.goto(page, FEED_URL)
            badge_after = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            moved = badge_after.get("pending") != badge_before.get("pending")
            print(f"    feed invitation badge AFTER: "
                  f"{badge_after.get('state')} {badge_after.get('pending')} "
                  f"-- {'MOVED' if moved else 'UNMOVED'}")
            if (badge_before.get("state") == "read"
                    and badge_before.get("pending") == 0 and not moved):
                print("    COST VERDICT: DEGENERATE. A badge at zero cannot "
                      "distinguish 'consumed nothing' from 'nothing to "
                      "consume'. This is NOT evidence the load is free.")

            await BROWSER.goto(page, CONTROL_URL)
            control_after = int(
                (await dom.read_surface_census(page)).get("controls_read") or 0
            )
            print(f"    control census AFTER: {control_after}")
    except Exception as error:  # noqa: BLE001
        print(f"\nRUN ABORTED: {type(error).__name__}: {error}")
        return 1
    finally:
        if page_ref is not None and not page_ref.is_closed():
            await page_ref.close()
        print("    tab closed:",
              page_ref.is_closed() if page_ref is not None else "no tab")

    print("\n=== VERDICT")
    floor = int(CONTROL_EXPECTED * 0.5)
    if control_before < floor or control_after < floor:
        print("    THE CONTROL FAILED. Nothing above is a reading about his "
              "account.")
        return 1
    print(f"    control {control_before} -> {control_after}, floor {floor} "
          "-- PASS at both ends")
    if verdict_rows is None or overlap is None:
        print("    NO SPLIT WAS PRODUCED.")
        return 1
    if verdict_rows["distinct"] != 5 or overlap["in_common"] != 0:
        print(f"    REFUSING TO PUBLISH. Four independent instruments say "
              f"FIVE memberships disjoint from five others; this walk says "
              f"{verdict_rows['distinct']} with {overlap['in_common']} in "
              "common. A disagreement here is a finding about THIS WALK.")
        return 1
    print("    FIVE distinct memberships, ZERO in common -- reproduces the "
          "validated split with NO page.evaluate.")
    print("    NAMES PUBLISHED BY THIS RUN: 0.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
