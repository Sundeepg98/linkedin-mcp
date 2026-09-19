"""WHICH of his items carries the reaction. Pairs it; never picks by position.

THE QUESTION. A reaction was fired on 2026-09-03 and landed -- ``performed
True, verified True, clicks_made 1`` -- and the urn it landed on was not kept.
``scripts/_probe_reaction_on_label.py`` established the next morning that the
profile rail draws EIGHT reaction controls, SEVEN wearing
``Reaction button state: no reaction`` and one wearing
``Reaction button state: Like``. So exactly one item is reacted and nothing
said which.

**THE OBVIOUS SHORTCUT IS THE ONE THING THIS PACKAGE REFUSES.** The activity
reader returns eight urns in document order and the rail draws eight reaction
controls in document order, so zipping the two lists by index would name an
item. That is choosing by position, it is refused everywhere here, and it
would be aiming an UN-REACT -- a write on a real post -- at whatever the
alignment happened to produce. Two lists agreeing in length is not a pairing.

**SO THE PAIRING IS STRUCTURAL.** For each reaction control that is NOT in the
off state, this climbs to the nearest ancestor that also contains an item
permalink anchor, and reads the urn out of THAT subtree. The control and the
urn come back from the same DOM node, so the answer is "this item's own
reaction control is on" rather than "the Nth control and the Nth urn". It is
the same climb ``dom.ACTIVITY_ITEMS_JS`` uses to pair a urn to an item root.

REFUSES RATHER THAN GUESSING, on every branch:

* no reacted control -> nothing to report, and it says so;
* a reacted control that climbs to no permalink -> reported as UNPAIRED, and
  no urn is invented for it;
* more than one distinct reacted urn -> ALL of them are printed and none is
  called "the" one. The fire was a single click, so two would mean either an
  older reaction nobody recorded or a pairing this probe got wrong, and both
  are things a human must look at before a write is aimed.

## Bounds and what it emits

ONE navigation, to a module constant. It clicks nothing and can perform
nothing; there is no un-react here and there could not be -- that is a write,
it belongs to the session holding the operator's authorisation for it, and a
probe that could fire it would be the wrong place for that button.

IT PRINTS A REAL URN, deliberately, because that is the deliverable. That
string addresses a real post: it must not be pasted into a tracked file in
this repository -- ``tests/test_no_committed_identity.py`` sweeps every
tracked file for exactly this shape and this repository is public. It is
printed to a transcript for a human to act on, and nothing here writes it to
disk.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.writes import PROFILE_URL  # noqa: E402

PAIR_JS = """
(cfg) => {
  const controls = Array.from(
    document.querySelectorAll('button[aria-label]')
  ).filter((n) =>
    (n.getAttribute('aria-label') || '').startsWith(cfg.statePrefix)
  );

  const reacted = controls.filter(
    (n) => (n.getAttribute('aria-label') || '') !== cfg.offLabel
  );

  // THE CLIMB. Walk up from the control until an ancestor contains an item
  // permalink, then take the urn out of that ancestor. Bounded so a page
  // whose structure changed cannot walk to <html> and pair the control with
  // whatever the first item on the rail happens to be.
  const pairs = [];
  let unpaired = 0;
  for (const control of reacted) {
    let node = control;
    let urn = null;
    for (let hops = 0; hops < cfg.maxHops && node; hops += 1) {
      const anchor = node.querySelector
        ? node.querySelector('a[href*="' + cfg.marker + '"]')
        : null;
      if (anchor) {
        const href = anchor.getAttribute('href') || '';
        const at = href.indexOf(cfg.marker);
        if (at !== -1) {
          const tail = href.slice(at + cfg.marker.length);
          const stop = tail.indexOf('/');
          urn = stop === -1 ? tail : tail.slice(0, stop);
        }
        break;
      }
      node = node.parentElement;
    }
    if (urn) {
      pairs.push({urn: urn, label: control.getAttribute('aria-label') || ''});
    } else {
      unpaired += 1;
    }
  }

  const distinct = [...new Set(pairs.map((p) => p.urn))];
  return {
    controls: controls.length,
    reacted: reacted.length,
    paired: pairs.length,
    unpaired: unpaired,
    distinct_urns: distinct.length,
    pairs: pairs,
  };
}
"""

#: How far to climb before giving up. The item root sits a few levels above
#: the control; anything much deeper means the rail was restructured and a
#: pairing would be a guess.
MAX_HOPS = 12


async def main() -> None:
    print("PROBE: which item carries the reaction")
    print(f"  off label:    {dom.REACTION_OFF_LABEL!r}")
    print(f"  state prefix: {dom.REACTION_STATE_PREFIX!r}")
    print("  pairs by CLIMB, never by index. Clicks nothing.\n")

    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, PROFILE_URL)
        print(f"  landed on /in/: {'/in/' in landed}")
        print(f"  self-assertion rode: {'isSelfProfile=true' in landed}\n")

        reading = await page.evaluate(
            PAIR_JS,
            {
                "statePrefix": dom.REACTION_STATE_PREFIX,
                "offLabel": dom.REACTION_OFF_LABEL,
                "marker": dom.ACTIVITY_PERMALINK_MARKER,
                "maxHops": MAX_HOPS,
            },
        )

        for key in ("controls", "reacted", "paired", "unpaired",
                    "distinct_urns"):
            print(f"    {key:16s} {reading.get(key)}")

        pairs = list(reading.get("pairs") or [])
        print()
        if int(reading.get("controls") or 0) == 0:
            # THE UNINTERPRETABLE ZERO, AND THIS BRANCH DID NOT EXIST ON THE
            # FIRST RUN. It printed "NOTHING IS REACTED on this rail" off a
            # page carrying ZERO reaction controls -- reporting a page that
            # never drew as a statement about reactions, which is the exact
            # absent-versus-zero conflation this wave has now found in three
            # other instruments. Measured 2026-09-04: controls 0 where the
            # same rail drew 8 an hour earlier, with the self-assertion also
            # absent on that load. The rail is non-deterministic; a zero from
            # it is a reading that failed.
            print("  THE RAIL DID NOT DRAW. Zero reaction controls, where")
            print("  this surface is measured to draw one per item. This says")
            print("  NOTHING about whether anything is reacted -- it is a")
            print("  reading that failed, not a count. Run it again.")
        elif int(reading.get("reacted") or 0) == 0:
            print("  THE RAIL DREW AND NOTHING ON IT IS REACTED. Every one of")
            print(f"  the {reading.get('controls')} controls wears the off label.")
            print("  Either the reaction was already undone, or it sits on an")
            print("  item this rail does not draw. No urn, and none invented.")
        elif int(reading.get("unpaired") or 0) and not pairs:
            print("  A REACTED CONTROL EXISTS AND CLIMBS TO NO PERMALINK.")
            print("  Reported as unpaired; no urn is guessed for it.")
        elif int(reading.get("distinct_urns") or 0) > 1:
            print("  MORE THAN ONE REACTED ITEM. All are printed and none is")
            print("  called 'the' one -- the fire was a single click, so this")
            print("  wants a human before any write is aimed.")
            for pair in pairs:
                print(f"    {pair['label']!r}  ->  {pair['urn']}")
        else:
            print("  THE REACTED ITEM:")
            for pair in pairs:
                print(f"    label : {pair['label']!r}")
                print(f"    urn   : {pair['urn']}")
            print()
            print("  Paired by climbing from the control to the ancestor that")
            print("  carries its own permalink, so the control and the urn")
            print("  came from one node rather than from two lists that")
            print("  happened to be the same length.")

        print("\n  REMINDER: that urn addresses a real post. Do not paste it")
        print("  into a tracked file -- test_no_committed_identity.py sweeps")
        print("  for exactly this shape and this repository is public.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    asyncio.run(main())
