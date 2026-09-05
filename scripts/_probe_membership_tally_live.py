"""The name-free membership reader, run against his real Groups page.

WHY THIS EXISTS AT ALL: ``shape.membership_row`` was written before any
consumer and still has none, and the note in its own docstring says so
plainly. A reader no caller can invoke is a hypothesis rather than a
capability -- ``tests/test_reader_reachability.py`` says exactly that about
``dom.py``, and the sentence does not stop being true one module over. So
``linkedin_server/groups.py`` ships WITH its first caller instead of waiting
for one.

## WHAT IT MEASURES, AND IT IS A THIRD INSTRUMENT RATHER THAN A REPLAY

The precondition was settled offline over a capture, by heading boundary and
by per-row control. This splits the same page LIVE and STRUCTURALLY, on the
rule ``_probe_groups_menu.py`` validated when it aimed its presses:

    For each group anchor, walk up to the first ancestor holding exactly one
    group anchor -- that ancestor is the ROW. A row containing a control that
    declares aria-expanded is a MEMBERSHIP row; one containing none is a
    SUGGESTION row. An anchor whose walk reaches a multi-anchor ancestor first
    has no row of its own and is counted separately rather than assigned.

No heading is read, no label is read, and no section name crosses. If this
agrees with the two offline signals, three instruments that share no input
feature agree.

## WHAT CROSSES BACK, AND THE ONE PLACE RAW STRINGS LIVE

Raw hrefs cross into this process and go STRAIGHT into
``groups.membership_tally``, which is the shaper for this path -- exactly the
placement argument ``dom.read_surface_census`` makes for accessible names: the
raw string has one exit and it is the reducer. Nothing else touches them.

**AND NOTHING PRINTS AN IDENTIFIER, NOT EVEN THOUGH THE MODULE PUBLISHES
ONE.** The module's contract is counts AND identifiers, because a caller
computing overlap needs them. A transcript is not that caller. So the split is
one level down from the boundary rule this repository already keeps:

    THE READER DECIDES WHAT IT RETURNS. THE CALLER DECIDES WHAT IT SAYS.

The operator's slug reached a transcript three times before the output sink
was added to the taint guard, and a group id is not a slug but the reasoning
that put it there does not depend on which identifier it was.

## THE EXCEPTION HANDLER AROUND THE EXTRACTION IS CLASS-ONLY, DELIBERATELY

Everywhere else in this repository a handler that drops the exception MESSAGE
is an anti-pattern, and it is named as one in the freeze ruling. This one
block is the exception and the reason is specific rather than general: it is
the only scope holding raw hrefs, and an interpolated traceback is precisely
how an identity url reached a transcript here before. Class-only inside the
block; full messages everywhere outside it.

## COST

The pending-invitation badge is read on the feed BEFORE and again after. It is
known from ``_probe_groups_menu.py`` that the groups page's own nav draws no
count-bearing mynetwork link, so the AFTER reading is taken back on the feed --
the page that carries the instrument. That costs one extra navigation and buys
a reading that can actually move.

Usage::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_membership_tally_live.py
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

#: THE SPLIT, done in the page. Returns hrefs in three buckets and nothing
#: else -- no label, no heading, no section name.
#:
#: **THE WALK STARTS AT THE CONTROL, AND RUN 1 PROVED THAT IS NOT A DETAIL.**
#: The first version of this file ran the identical stopping rule from the
#: ANCHOR and found ZERO membership rows, against FIVE from
#: ``_probe_groups_menu.py`` running it from the BUTTON on the same page in
#: the same hour. Two directions, one rule, 5 and 0.
#:
#: The cause is that "the first ancestor holding exactly one group anchor" is
#: not a definition of A ROW. It is a definition of THE SMALLEST ELEMENT
#: CONTAINING WHAT YOU STARTED FROM, and those coincide only when the start
#: point is outside the anchor's own subtree. From the button you must climb
#: past the button's branch to reach the anchor, so you land on their common
#: parent -- the row. From the anchor you stop at its own tight wrapper, which
#: contains no control at all, and every row reads as a suggestion.
#:
#: **A CONTAINMENT RULE IS NOT SYMMETRIC**, and this project has paid for the
#: neighbouring lesson once already: a budget on how FAR a walk goes is not a
#: rule about WHERE it stops. This is the other half -- a rule about where it
#: stops is not complete until it says WHERE IT STARTS.
#:
#: So the validated direction is kept and the anchor is DERIVED from it: for
#: each row-scoped control, the one group anchor inside its stopping ancestor
#: is the membership href. Everything else with a group segment is a
#: suggestion or the root.
SPLIT_JS = """
(cfg) => {
  const isGroup = (a) => {
    let path = '';
    try { path = new URL(a.href, document.baseURI).pathname; }
    catch (e) { return false; }
    return path.indexOf(cfg.marker) !== -1;
  };
  const groupAnchors = (root) =>
    Array.from(root.querySelectorAll('a[href]')).filter(isGroup);

  const anchors = groupAnchors(document);
  const buttons = Array.from(document.querySelectorAll(cfg.selector));
  const with_control = [];
  const claimed = new Set();
  let rows_found = 0;
  let rows_sharing_an_anchor = 0;

  buttons.forEach((button) => {
    let node = button.parentElement;
    let row = null;
    while (node) {
      const found = groupAnchors(node).length;
      if (found === 1) { row = node; break; }
      if (found > 1) { break; }
      node = node.parentElement;
    }
    if (!row) return;
    rows_found += 1;
    const anchor = groupAnchors(row)[0];
    // TWO CONTROLS IN ONE ROW MUST NOT COUNT THE ROW TWICE. Counted and
    // reported rather than silently de-duplicated, because a row drawing two
    // disclosures is a fact about the page a reader should see.
    if (claimed.has(anchor)) { rows_sharing_an_anchor += 1; return; }
    claimed.add(anchor);
    with_control.push(anchor.getAttribute('href'));
  });

  const without_control = [];
  anchors.forEach((anchor) => {
    if (!claimed.has(anchor)) without_control.push(anchor.getAttribute('href'));
  });

  return {
    anchors: anchors.length,
    buttons: buttons.length,
    rows_found: rows_found,
    rows_sharing_an_anchor: rows_sharing_an_anchor,
    with_control: with_control,
    without_control: without_control,
    no_row: [],
  };
}
"""


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print("    A launch-mode session would open a SECOND Chrome on the "
              "operator's own profile and DOWNGRADE it.")
        return 2

    if not readonly.is_read_url(GROUPS_URL):
        print("REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    print("=== THE NAME-FREE MEMBERSHIP READER, ON HIS REAL GROUPS PAGE")
    print("    Splits the page STRUCTURALLY. No heading and no label is read.")
    print("    Prints COUNTS ONLY -- the module publishes identifiers, this "
          "caller does not say them.")

    page_ref = None
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
            print(f"\n    control census: {control_before}, expected about "
                  f"{CONTROL_EXPECTED}")
            print(f"    invitation badge on the feed BEFORE: "
                  f"{badge_before.get('state')} {badge_before.get('pending')}")

            landed = await BROWSER.goto(page, GROUPS_URL)
            served = str(landed).rstrip("/") == GROUPS_URL.rstrip("/")
            walled = "/login" in str(landed) or "/checkpoint" in str(landed)
            print(f"    served the address asked for: {served}")
            if walled:
                print("    AUTH WALL. Nothing measured.")
                return 1

            split = await page.evaluate(
                SPLIT_JS,
                {"marker": "/groups/", "selector": "button[aria-expanded]"},
            )

            # THE ONLY SCOPE HOLDING RAW HREFS. Class-only handler, and the
            # module docstring argues that exception rather than assuming it.
            try:
                membership = groups.membership_tally(
                    split.get("with_control") or []
                )
                suggestion = groups.membership_tally(
                    split.get("without_control") or []
                )
                orphan = groups.membership_tally(split.get("no_row") or [])
                overlap = groups.disjoint(
                    split.get("with_control") or [],
                    split.get("without_control") or [],
                )
            except Exception as error:  # noqa: BLE001
                print(f"    THE REDUCER RAISED: {type(error).__name__}. The "
                      "message is withheld because this scope holds raw "
                      "hrefs and an interpolated traceback is how an identity "
                      "url reached a transcript here before.")
                return 1

            print(f"\n=== ANCHORS: {split.get('anchors')} whose path carries "
                  "the group segment")
            print(f"    disclosure controls on the page: "
                  f"{split.get('buttons')}, of which "
                  f"{split.get('rows_found')} are row-scoped; "
                  f"{split.get('rows_sharing_an_anchor')} shared a row with "
                  "another control")
            for name, tally in (
                ("ROWS WITH a row-scoped control", membership),
                ("ROWS WITHOUT one", suggestion),
                ("ANCHORS WITH NO ROW OF THEIR OWN", orphan),
            ):
                print(f"    {name}:")
                print(f"        rows {tally['rows']}, identified as groups "
                      f"{tally['groups']}, DISTINCT {tally['distinct']}")
                print(f"        refused: {tally['refused'] or 'none'}")

            print("\n=== ARE THEY TWO SETS OR ONE SET DRAWN TWICE?")
            print(f"    first {overlap['first_distinct']}, second "
                  f"{overlap['second_distinct']}, in common "
                  f"{overlap['in_common']}, DISJOINT {overlap['disjoint']}")

            badge_after_page = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            print(f"\n    invitation badge on the GROUPS page: "
                  f"{badge_after_page.get('state')} "
                  f"{dict(badge_after_page.get('saw') or {})}")
            await BROWSER.goto(page, FEED_URL)
            badge_after = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            print(f"    invitation badge on the feed AFTER: "
                  f"{badge_after.get('state')} {badge_after.get('pending')} -- "
                  f"{'UNMOVED' if badge_after.get('pending') == badge_before.get('pending') else 'MOVED'}")

            await BROWSER.goto(page, CONTROL_URL)
            control_after = int(
                (await dom.read_surface_census(page)).get("controls_read") or 0
            )
            print(f"    control census at the END: {control_after}")
    except Exception as error:  # noqa: BLE001
        print(f"\nRUN ABORTED: {type(error).__name__}: {error}")
        return 1
    # CLOSE THE TAB THIS RUN OPENED. Measured 2026-09-05: in ATTACH mode
    # ``BROWSER.session()`` calls ``ctx.new_page()`` and its own ``finally``
    # only touches an idle timer, so **every probe run leaves a tab open on the
    # operator's browser.** Twenty-four had accumulated across the fleet, and
    # ``connect_over_cdp`` enumerates every target during the handshake, which
    # is why attach was timing out for everybody.
    #
    # THE FIX BELONGS HERE AND NOT IN ``browser.py``, and the difference is
    # LIFETIME rather than code: the MCP server keeps its page ACROSS tool
    # calls on purpose, so closing centrally would cost a fresh tab per call
    # and throw that reuse away. A probe is a one-shot and has nothing to keep.
    #
    # In a ``finally``, so a run that ABORTS still cleans up -- the aborting
    # runs are exactly the ones that were leaking.
    finally:
        if page_ref is not None and not page_ref.is_closed():
            await page_ref.close()

    print("\n=== VERDICT")
    floor = int(CONTROL_EXPECTED * 0.5)
    if control_before < floor or control_after < floor:
        print("    THE CONTROL FAILED. Nothing above is a reading about his "
              "account.")
        return 1
    print(f"    control {control_before} -> {control_after}, floor {floor} -- "
          "PASS at both ends")
    if membership["distinct"] == 0:
        print("    ZERO memberships by this rule, against five from two "
              "offline instruments. THREE instruments do not agree and the "
              "disagreement is the finding -- do not read any count here as "
              "his membership count.")
        return 1
    print(f"    memberships by the structural rule: {membership['distinct']} "
          f"distinct")
    print("    NAMES PUBLISHED BY THIS RUN: 0. The reader is never handed "
          "one, so there is no filter to have got wrong.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
