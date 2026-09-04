"""The ON label the first reaction was supposed to produce, and did not report.

THE FIRE LANDED AND ITS MEASUREMENT DID NOT ARRIVE. ``react_to_item`` was
performed on one of his own items: ``performed True, verified True,
clicks_made 1``. Its own ``reversibility_procedure`` said that firing would
settle the open question -- "React to one item and READ THE LABEL THE CONTROL
CHANGES INTO. That single string settles both halves at once -- it is the
anchor for the inverse action and the evidence that an action landed." The
result carried no such label, and ``to_undo`` still reads "UNKNOWN ... with the
ON label unmeasured there is no selector for the inverse."

So a reaction now sits on his post that this server cannot remove.

## WHY IT DID NOT ARRIVE -- read off the source before this probe was written

``writes.py`` verifies the reaction like this::

    reading = await dom.read_reaction_surface(page)
    controls = int(reading.get("controls") or 0)
    off = int(reading.get("off_state") or 0)

and then decides on those two counts alone. **``read_reaction_surface`` also
returns ``labels``** -- the DISTINCT accessible names of every reaction control
it read, each already put through ``shape.census_shape``. The verification
never touches that key.

So the hypothesis this probe tests is not "the reader looks in the wrong
place". It is worse and cheaper to fix: **the label was very likely read and
discarded on the very call that was supposed to measure it.**

The competing hypothesis is that the control does not rename itself the way
the spec assumed -- that a reacted control keeps saying "no reaction", or stops
carrying an ``aria-label`` at all. That would make the verification's
``off == 0`` test unsound as well, which is why this is worth one page load.

## Why /in/me/ rather than the item permalink

His profile rail draws ONE reaction control per item -- measured at 8 on
2026-08-30, every one of them then in the OFF state. Reading the rail answers
the question for every item at once and does not require knowing WHICH urn was
reacted, so no identifier has to be carried into this file to run it.

If exactly one item is reacted, ``labels`` comes back with TWO distinct
strings and ``off_state`` reads one less than ``controls``. That is the whole
measurement.

## What it emits

Counts, and the SHAPED labels ``read_reaction_surface`` already produces.
Shaping is not optional politeness here: LinkedIn writes a member's name into
the neighbouring ``Hide post by <name>`` control, so an unshaped label read is
one LinkedIn rename away from pulling a third party's identity into a
transcript. Every string printed below has been through ``census_shape``.

## Bounds

ONE navigation, to a module constant. Clicks nothing, types nothing, presses
nothing. It cannot un-react and does not try.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.writes import PROFILE_URL  # noqa: E402


async def main() -> None:
    print("PROBE: what label does a REACTED control wear?")
    print(f"  off label on record: {dom.REACTION_OFF_LABEL!r}")
    print(f"  state prefix:        {dom.REACTION_STATE_PREFIX!r}")
    print("  emits counts and SHAPED labels only.\n")

    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, PROFILE_URL)
        print(f"  landed on /in/: {'/in/' in landed}")
        print(f"  self-assertion rode: {'isSelfProfile=true' in landed}\n")

        reading = await dom.read_reaction_surface(page)

        print("=== read_reaction_surface")
        for key in ("controls", "off_state", "menus", "comment_controls",
                    "permalinks"):
            print(f"    {key:20s} {reading.get(key)}")

        labels = list(reading.get("labels") or [])
        print(f"\n    labels ({len(labels)} distinct, already shaped):")
        for label in labels:
            print(f"      {label!r}")

        controls = int(reading.get("controls") or 0)
        off = int(reading.get("off_state") or 0)
        on = controls - off

        print("\n=== HOW TO READ THIS")
        print(f"    controls {controls}, off {off}, so NOT-off = {on}.")
        if controls == 0:
            print("    ZERO CONTROLS -- the rail did not draw. This says")
            print("      nothing about any reaction; run it again.")
        elif on == 0:
            print("    NOTHING IS REACTED on this rail. Either the fire did")
            print("      not land where this looks, or it was already undone.")
            print("      The ON label stays unmeasured and the inverse stays")
            print("      unaimable -- do NOT guess it.")
        elif len(labels) >= 2:
            print("    THE ON LABEL IS ABOVE. The distinct label that is not")
            print(f"      {dom.REACTION_OFF_LABEL!r} is what a reacted control")
            print("      wears. That is the anchor the inverse selector needs,")
            print("      and it was sitting in reading['labels'] all along --")
            print("      the verification reads only controls and off_state.")
            print("      Surfacing this key is the whole repair.")
        else:
            print("    NOT-off is nonzero but only ONE distinct label came")
            print("      back. That means the reacted control carries no")
            print("      aria-label at all, or one that shaped to the same")
            print("      string -- in which case off_state is counting")
            print("      something other than what it is assumed to, and the")
            print("      verification's `off == 0` test needs re-examining.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    asyncio.run(main())
