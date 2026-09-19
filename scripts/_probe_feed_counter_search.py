"""IS THERE A COUNTER ON /feed/ THAT COULD PRICE A PRESS? One read, no press.

Condition 3 of the disclosing-press ruling says a press must be SHOWN not to
move an outward counter, and that **where no counter can price a press,
unmeasurable resolves AGAINST it.** A wave reported that the nav badges moved
for neither of two feed presses and flagged that this might refuse most
feed-item presses by default.

**ONE WAVE'S READ OF ONE PAGE IS NOT AN EXHAUSTIVE SEARCH FOR A COUNTER**, and
the nav badges are the wrong instrument anyway: they count invitations and
unread messages, neither of which a feed press could plausibly move. A badge
that cannot move for the act in question prices nothing -- this repository
already records the trap in its sibling form, that *a badge at zero cannot
distinguish "the page consumed nothing" from "there was nothing to consume".*

So this looks for counters of a DIFFERENT CLASS: per-control STATE on the page
already loaded, rather than a global badge somewhere else.

    read_reaction_surface  controls / off_state / comment_controls
    shape.save_state       a save control's on-or-off state
    shape.follow_state     a follow control's on-or-off state

**WHY THOSE THREE ARE THE RIGHT CANDIDATES.** A feed overflow menu is a
plausible home for Save, Unfollow, Hide and Report. If a press did any of them,
the corresponding control's STATE flips -- and a reaction, a save and a follow
are all outward in the sense that matters: a reaction is visible to the post's
author, and the other two persist on his account.

**AND TWO CANDIDATES ARE ALREADY RULED OUT WITHOUT A LOAD**, which is why they
are not in this probe: `/my-items/saved-posts/` and `/my-items/` are REFUSED by
the read boundary, so a saved-items count is unreachable; and `/notifications/`
is admitted but has no reader in this package and is measured to reset its own
badge on load, so pricing a press with it would spend the thing being counted.

**WHAT WOULD MAKE A COUNTER USABLE**, and it is the whole question: it must be
NON-ZERO, because a counter reading zero on an unpressed page cannot be shown
to have been able to move. This probe therefore reports the counts and nothing
else -- it does not press, so it cannot and does not claim any of them DOES
move.

Run:  LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
      ./venv/Scripts/python.exe scripts/_probe_feed_counter_search.py

Presses NOTHING. Types NOTHING. Sends NOTHING. Hovers over NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL  # noqa: E402

#: Candidate STATE counters, as selectors written in this file. Every one is an
#: attribute or role selector; none reads a label into a decision.
#:
#: THE FIRST IS THE FIRING CONTROL. A logged-in feed draws buttons; if that
#: reads zero the reader is dead and every other zero here is void.
_CANDIDATES: tuple[tuple[str, str], ...] = (
    ("CONTROL button", "button"),
    ("feed update containers", "div[data-urn]"),
    ("aria-pressed present", "[aria-pressed]"),
    ("aria-pressed=false", '[aria-pressed="false"]'),
    ("aria-pressed=true", '[aria-pressed="true"]'),
    ("aria-checked present", "[aria-checked]"),
    ("overflow triggers", '[aria-expanded="false"]'),
    ("menu triggers", "[aria-haspopup]"),
)


async def _count(page, selector: str):
    """A count, or None when the reader failed.

    **None is NOT zero and is never reported as one.** An exception here is an
    outage or a bad selector, and either is a fact about the instrument rather
    than about LinkedIn -- filing it as a zero is how an outage becomes an
    absence.
    """
    try:
        return int(await page.locator(selector).count())
    except Exception as exc:  # noqa: BLE001
        print("      reader failed: %s" % type(exc).__name__)
        return None


async def _run(page) -> None:
    print("\n1. THE READ -- /feed/ only, and nothing is pressed")
    landed = await BROWSER.goto(page, FEED_URL)
    if "/login" in landed or "/checkpoint" in landed:
        print("    AUTH WALL. Nothing measured.")
        return

    surface = await dom.read_thread_reply_surface(page)
    print("    elements on the page: %r" % surface.get("elements"))
    print("    settle verdict:       %r" % surface.get("settle"))
    if surface.get("settle") == "unrendered":
        print("    STOP. The page did not render; every count below is about")
        print("    that and not about LinkedIn.")
        return

    print("\n2. THE SHIPPED REACTION READER (scalars only, no labels)")
    reaction = await dom.read_reaction_surface(page)
    for key in ("controls", "off_state", "menus", "comment_controls", "permalinks"):
        print("      %-22s %r" % (key, reaction.get(key)))
    print("      (off_state is the candidate: a control in the OFF state that")
    print("       later reads ON means something reacted. A reaction is")
    print("       visible to the post's author, which is what makes it an")
    print("       OUTWARD counter rather than a render detail.)")

    print("\n3. PER-CONTROL STATE CANDIDATES")
    control_alive = True
    for label, selector in _CANDIDATES:
        value = await _count(page, selector)
        if label.startswith("CONTROL") and not value:
            control_alive = False
        print("      %-24s %r" % (label, value))

    print()
    if not control_alive:
        print("    THE CONTROL DID NOT FIRE. Every count above is void.")
        return
    print("    HOW TO READ THIS. A counter is USABLE for condition 3 only if")
    print("    it is NON-ZERO here: a counter that reads zero on an unpressed")
    print("    page cannot be shown to have been able to move, and a reading")
    print("    that cannot move proves nothing about a press that did not")
    print("    move it. This probe presses nothing, so it establishes")
    print("    AVAILABILITY and never behaviour.")


async def main() -> None:
    print("=" * 72)
    print("FEED COUNTER SEARCH -- can anything here price a press?")
    print("=" * 72)
    async with BROWSER.session() as page:
        try:
            await _run(page)
        finally:
            try:
                await page.close()
                print("\n    page closed: %r" % page.is_closed())
            except Exception as exc:  # noqa: BLE001
                print("\n    page close failed: %s" % type(exc).__name__)
            print("    presses: 0   hovers: 0   types: 0   sends: 0")


if __name__ == "__main__":
    asyncio.run(main())
