"""What can be DONE to a group from the one address this server may open?

# ===================================================================
# STATUS: RUN GREEN. Its own control AGREES, and it did NOT at first.
# ===================================================================
#
# HISTORY, kept because the failures are the evidence that the control works:
#
#   16:52-17:07  FIVE attach attempts, all aborted in the CDP handshake at the
#                hardcoded 15s ceiling while the browser was measured healthy
#                (port listening, /json/version answering in 0.07s, the process
#                alive). Root-caused: 120 CDP targets on a browser shared by a
#                dozen waves, every one enumerated during the handshake.
#                NOTHING WAS KILLED OR RESTARTED to get around it.
#   17:10        LINKEDIN_CDP_ATTACH_TIMEOUT_MS added; this file ran.
#   17:17        FIRST READING, AND ITS OWN CONTROL FAILED: 11 anchors, 11
#                rows, ZERO carrying a disclosure, against FIVE from the
#                button-up walk. Printed DISAGREE and did not publish the zero.
#   17:29        After the fix below: 11 anchors, 10 rows, FIVE with a
#                disclosure and five without. AGREE.
#
# THE DEFECT THE CONTROL CAUGHT, and it is the reason the control was written
# before the reading was taken: the control selector includes ``a[href]``, so
# THE GROUP ANCHOR THE WALK CLIMBS FROM SATISFIED "this ancestor holds at least
# one control" BY ITSELF. The conjunct that was supposed to make this rule
# stricter than the anchor-up walk was VACUOUS, and the rule silently collapsed
# back into the walk that had already been measured wrong.
#
#     A CONJUNCT THAT IS ALWAYS TRUE IS NOT A STRICTER RULE. It is the same
#     rule with a longer comment -- and it reads, in a diff, exactly like the
#     repair it is not.
#
# Nothing but the control separated the two. The output of the broken rule --
# eleven rows, no disclosures -- is a perfectly plausible page.

TWENTY OF ``GROUPS-SURFACE``'S THIRTY-TWO ROWS ARE WRITES, and every one of
them was costed off a page nobody had opened. ``_probe_groups_menu.py`` opened
the five overflow menus and found three affordances. **That is not the whole
answer, because it only looked at rows that HAVE an overflow menu** -- which is
exactly the five memberships. The five suggestion rows have no such control,
and the join rows (``N 63``, ``N 163``, ``M C61``) live on those.

So this asks the complementary question: for EVERY group row on the root,
membership and suggestion alike, what controls does LinkedIn draw?

## THE STOPPING RULE, AND IT IS THE THIRD VERSION OF IT

``_probe_membership_tally_live.py`` measured that the same containment rule run
from the anchor and from the button gives 0 and 5, because *"the first ancestor
holding exactly one group anchor"* names the smallest element containing WHAT
YOU STARTED FROM rather than a row. A suggestion row has no button to start
from, so that repair is unavailable here and a third rule is needed:

    Walk up from the anchor to the first ancestor that holds exactly one group
    anchor AND at least one control. Stop there. If an ancestor holding more
    than one group anchor is reached first, the anchor has no row of its own.

**A ROW IS THE SMALLEST THING THAT HOLDS ONE GROUP AND SOMETHING TO DO TO IT
THAT IS NOT THE GROUP LINK ITSELF.** The last clause is not pedantry -- it is
the whole difference between this rule and the one it replaces, and leaving it
out is what the STATUS block above records failing.

This probe reports the count it finds per class so a reader can see it agreeing
with the button-up walk rather than take it on trust: **five rows carrying a
disclosure is the number to check against.**

## WHAT IT ANSWERED, 2026-09-05 at 17:29 IST -- AND THE ANSWER IS AN ABSENCE

    ROWS WITH A DISCLOSURE (memberships)   5   'Update your settings'  x5
    ROWS WITHOUT ONE (suggestions)         5   nothing repeats at all

**NO CONTROL IS DRAWN UNIFORMLY ACROSS THE SUGGESTION ROWS**, and that is how
an absence becomes a measurement here rather than a shrug. A join affordance
would wear one label on every suggestion row -- exactly as `Update your
settings` does on every membership row -- so it would tally 5 and survive the
count rule. Every suggestion-row label tallied ONE and was redacted as a
singleton, which is what a label carrying a group's own name does.

So `N 63`, `N 163` and `M C61` -- join, request to join -- are NOT reachable
from this admitted address. They need `/groups/<id>/` or `/groups/discover/`,
and neither is on the allowlist.

## LABELS ARE SHAPED AND COUNT-REDACTED, and the tally is real

Every control label crosses raw and is reduced here by ``census_shape`` then
``census_redact_rare`` with its own tally across all rows. A verb LinkedIn
draws on every row of a class survives; a label carrying one group's name is a
singleton and is redacted with no special case. That is the same instrument
``_probe_groups_menu.py`` used on the menu contents, pointed at the rows.

Nothing is pressed. Nothing is clicked. No menu is opened.

## COST

Feed BEFORE, feed AFTER -- the groups page's own nav draws no count-bearing
mynetwork link, measured, so an after-reading taken there would be a refusal
compared against a reading, and two refusals are not a pair.

Usage::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_group_row_affordances.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

GROUPS_URL = f"{BASE_URL}/groups/"
CONTROL_URL = f"{BASE_URL}/mypreferences/d/dark-mode"
CONTROL_EXPECTED = 20

ROWS_JS = """
(cfg) => {
  const isGroup = (a) => {
    let path = '';
    try { path = new URL(a.href, document.baseURI).pathname; }
    catch (e) { return false; }
    return path.indexOf(cfg.marker) !== -1 &&
           path.replace(/\\/+$/, '') !== cfg.rootPath;
  };
  const groupAnchors = (root) =>
    Array.from(root.querySelectorAll('a[href]')).filter(isGroup);
  // THE GROUP ANCHOR IS NOT ONE OF THE ROW'S CONTROLS, AND RUN 1 SHIPPED
  // BELIEVING IT WAS. The control selector includes ``a[href]``, so the very
  // anchor the walk is climbing from satisfied "this ancestor holds at least
  // one control" -- the added conjunct was VACUOUS, the rule collapsed back
  // into the anchor-up walk, and it resolved 11 rows of which 0 carried a
  // disclosure. **A conjunct that is always true is not a stricter rule; it
  // is the same rule with a longer comment.**
  const controlsIn = (root) => {
    const own = new Set(groupAnchors(root));
    return Array.from(root.querySelectorAll(cfg.controls))
                .filter((n) => !own.has(n));
  };

  const anchors = groupAnchors(document);
  const rows = [];
  let no_row = 0;

  anchors.forEach((anchor) => {
    let node = anchor.parentElement;
    let row = null;
    while (node) {
      const found = groupAnchors(node).length;
      if (found > 1) break;
      if (found === 1 && controlsIn(node).length > 0) { row = node; break; }
      node = node.parentElement;
    }
    if (!row) { no_row += 1; return; }
    const controls = controlsIn(row);
    rows.push({
      disclosures: controls.filter(
        (n) => n.getAttribute('aria-expanded') !== null
      ).length,
      labels: controls.map(
        (n) => (n.getAttribute('aria-label') || n.textContent || '').trim()
      ),
      links: row.querySelectorAll('a[href]').length,
    });
  });

  return {anchors: anchors.length, no_row: no_row, rows: rows};
}
"""


def _report(title: str, rows: list[dict]) -> None:
    print(f"\n    {title}: {len(rows)} rows")
    if not rows:
        return
    tally: dict[str, int] = {}
    for row in rows:
        for label in row["labels"]:
            tally[label] = tally.get(label, 0) + 1
    for label, count in sorted(tally.items(), key=lambda i: (-i[1], i[0])):
        safe = shape.census_redact_rare(shape.census_shape(label), count)
        print(f"        {count:>3}  {safe!r}")


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set. A launch-mode session "
              "would open a SECOND Chrome on the operator's own profile.")
        return 2
    if not readonly.is_read_url(GROUPS_URL):
        print("REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    print("=== WHAT DOES LINKEDIN DRAW ON EACH GROUP ROW?")
    print("    Nothing is pressed. Labels are shaped and count-redacted.")

    page_ref = None
    try:
        async with BROWSER.session() as page:
            page_ref = page
            await BROWSER.goto(page, CONTROL_URL)
            control_before = int(
                (await dom.read_surface_census(page)).get("controls_read") or 0
            )
            await BROWSER.goto(page, FEED_URL)
            before = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            print(f"\n    control census {control_before}, badge on the feed "
                  f"{before.get('state')} {before.get('pending')}")

            landed = await BROWSER.goto(page, GROUPS_URL)
            served = str(landed).rstrip("/") == GROUPS_URL.rstrip("/")
            walled = "/login" in str(landed) or "/checkpoint" in str(landed)
            print(f"    served the address asked for: {served}")
            if walled:
                print("    AUTH WALL. Nothing measured.")
                return 1

            reading = await page.evaluate(
                ROWS_JS,
                {
                    "marker": "/groups/",
                    "rootPath": "/groups",
                    "controls": "button, a[href], input",
                },
            )
            rows = list(reading.get("rows") or [])
            with_menu = [row for row in rows if row["disclosures"] > 0]
            without = [row for row in rows if row["disclosures"] == 0]

            print(f"\n=== {reading.get('anchors')} group anchors, "
                  f"{len(rows)} resolved to a row, "
                  f"{reading.get('no_row')} with no row of their own")
            print(f"    rows carrying a disclosure: {len(with_menu)} "
                  f"-- the button-up walk found 5, so "
                  f"{'AGREE' if len(with_menu) == 5 else 'DISAGREE'}")
            _report("ROWS WITH A DISCLOSURE (his memberships)", with_menu)
            _report("ROWS WITHOUT ONE (LinkedIn's suggestions)", without)

            await BROWSER.goto(page, FEED_URL)
            after = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            print(f"\n    badge on the feed AFTER: {after.get('state')} "
                  f"{after.get('pending')} -- "
                  f"{'UNMOVED' if after.get('pending') == before.get('pending') else 'MOVED'}")
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

    floor = int(CONTROL_EXPECTED * 0.5)
    print("\n=== VERDICT")
    if control_before < floor or control_after < floor:
        print("    THE CONTROL FAILED. Nothing above is a reading.")
        return 1
    print(f"    control {control_before} -> {control_after}, floor {floor} -- "
          "PASS at both ends")
    if not rows:
        print("    NO ROW RESOLVED. That is a finding about this stopping "
              "rule, not about the page -- two other instruments found ten "
              "group anchors here.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
