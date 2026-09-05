"""What is inside the one control an event row carries? ONE PRESS, and why.

THE ROOT DRAWS EXACTLY ONE CONTROL PER EVENT ROW and it is not an RSVP. The
strings ``Attend``, ``Interested``, ``Going`` and ``Register`` occur ZERO times
in 1294108 characters of the capture. What each of the 18 rows carries instead
is a single ``<button>`` with these class tokens, measured on all 18:

    artdeco-dropdown__trigger
    artdeco-dropdown__trigger--placement-bottom
    events-components-shared-support-share__share-button
    artdeco-button artdeco-button--secondary artdeco-button--circle

It is a DISCLOSURE WIDGET: it carries ``aria-expanded``, its inner content is
one 317-character ``svg``, and ``role="menu"`` and ``role="dialog"`` occur zero
times in the document. **So the menu is not in the DOM until it is pressed**,
and no amount of offline analysis can say what is in it.

## WHY THIS PRESS IS TAKEN WHEN THE GROUPS WAVE DECLINED ITS EQUIVALENT

That wave declined a press on a row control of a group HE BELONGS TO, in order
to read a membership label it did not need. This is a different act:

* the press is on a RECOMMENDATION row -- an event he has no relationship
  with, drawn by LinkedIn on a page it chose to show him;
* it opens a local menu and sends nothing. ``SANCTIONED_MUTATIONS``'s second
  entry already settles this class of act in this repository's own words --
  *a pill SENDS NOTHING and CHANGES NOTHING on LinkedIn's servers; it alters
  which rows are displayed. Counted by EFFECT rather than by verb, a view
  filter is a read.* A disclosure widget is the same category;
* and it is the ONLY route to a census row that is otherwise costed blind.
  ``N 193`` is "share an event you are attending with your network", and this
  is the share control. Costing a WriteSpec against a menu nobody has opened
  is the mistake this file exists to avoid.

**NOTHING INSIDE THE MENU IS PRESSED.** One press, on the trigger, then the
items are read and the run navigates away. The menu is left open exactly as
long as it takes to enumerate it.

## THE AIM IS AT A CLASS, NOT AT A POSITION, AND THE DIFFERENCE IS STATED

Eighteen buttons carry that class token and they are homogeneous by
construction -- one per row, same tokens, same inner svg. So a choice among
them is arbitrary BY DESIGN, and this file says so rather than dressing
``.first`` up as a decision. What it refuses to do is aim at an unqualified
position: if the trigger count is not 18 the run REFUSES, because a page that
draws a different number of them is not the page this reasoning was written
against.

## WHAT LEAVES THIS PROCESS

Counts, class tokens, and menu item labels through ``census_shape`` then
``census_redact_rare`` fed each label's real count among the items. A share
menu names DESTINATIONS (a feed, a message, a link) rather than people, but
that is a prediction and the shaping is what makes it safe to be wrong.

Usage::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_events_row_menu.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, events, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

EVENTS_URL = f"{BASE_URL}/events/"

#: The control, aimed by its own class token. Not by position among buttons,
#: and not by aria-label -- the labels are event titles, which is to say they
#: are the page's content and not this control's identity.
TRIGGER_SELECTOR = (
    'button[class~="events-components-shared-support-share__share-button"]'
)

#: MEASURED. If the page draws a different number, the reasoning above does
#: not apply to it and this refuses.
TRIGGER_EXPECTED = 18

#: Where a menu shows up once something is pressed. Read BEFORE and AFTER, so
#: the press is shown to have caused the difference rather than assumed to.
MENU_SELECTORS = (
    '[role="menu"]',
    '[role="dialog"]',
    "div[class~=artdeco-dropdown__content]",
)

#: What the menu's items are, once there is a menu.
ITEM_SELECTORS = (
    '[role="menuitem"]',
    "div[class~=artdeco-dropdown__content] button",
    "div[class~=artdeco-dropdown__content] a",
)


async def _tally(page, label: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for selector in MENU_SELECTORS + ITEM_SELECTORS:
        try:
            out[selector] = int(await page.locator(selector).count())
        except Exception:  # noqa: BLE001
            out[selector] = -1
    print(f"    {label}:")
    for selector, count in out.items():
        print(f"        {count:>4}  {selector}")
    return out


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set. This attaches to the")
        print("    operator's Chrome; a launch would open a second one on the")
        print("    same profile, one major version behind it.")
        return 2
    if not readonly.is_read_url(EVENTS_URL):
        print("REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    print("=== ONE PRESS ON ONE EVENT ROW'S ONLY CONTROL")
    try:
        async with BROWSER.session() as page:
            landed = await BROWSER.goto(page, EVENTS_URL)
            if "/login" in str(landed) or "/checkpoint" in str(landed):
                print("    AUTH WALL. Nothing here is a reading.")
                return 1

            reading = await events.read_events_home(page)
            print(f"    cards_read={reading['cards_read']} "
                  f"rows_total={reading['rows_total']} "
                  f"verdict={reading['verdict']}")

            triggers = page.locator(TRIGGER_SELECTOR)
            count = int(await triggers.count())
            print(f"    share triggers on the page: {count} "
                  f"(expected {TRIGGER_EXPECTED})")
            if count != TRIGGER_EXPECTED:
                print("    REFUSED. A page drawing a different number of this")
                print("    control is not the page this file reasons about.")
                return 1

            expanded_before = await triggers.first.get_attribute(
                "aria-expanded"
            )
            before = await _tally(page, "BEFORE THE PRESS")

            # THE PRESS. One, on the trigger, nothing inside the menu.
            await triggers.first.click(timeout=5_000)

            expanded_after = await triggers.first.get_attribute("aria-expanded")
            print(f"    aria-expanded: {expanded_before!r} -> "
                  f"{expanded_after!r}")
            after = await _tally(page, "AFTER THE PRESS")

            moved = [
                selector for selector in before
                if after.get(selector, -1) != before.get(selector, -1)
            ]
            print(f"    selectors whose count moved: {len(moved)}")
            if not moved:
                print("    THE PRESS CHANGED NOTHING THIS READER CAN SEE.")
                print("    That is a fact about these selectors, not proof")
                print("    the menu is empty -- and it is reported as such.")

            # THE ITEMS, shaped, with their real counts.
            labels: list[str] = []
            for selector in ITEM_SELECTORS + ('[role="menuitem"]',):
                try:
                    items = page.locator(selector)
                    for index in range(int(await items.count())):
                        text = (
                            await items.nth(index).inner_text(timeout=2_000)
                            or ""
                        ).strip()
                        if text:
                            labels.append(text)
                except Exception:  # noqa: BLE001
                    continue
            tally: dict[str, int] = {}
            for text in labels:
                tally[text] = tally.get(text, 0) + 1
            print(f"    MENU ITEM LABELS ({len(labels)} read, "
                  f"{len(tally)} distinct), shaped:")
            for text, occurrences in sorted(
                tally.items(), key=lambda item: (-item[1], item[0])
            ):
                shaped = shape.census_redact_rare(
                    shape.census_shape(text), occurrences
                )
                print(f"        {occurrences:>3}  {shaped!r}")

            census = await dom.read_surface_census(page)
            print(f"    controls_read on the page after the press: "
                  f"{census.get('controls_read')}")

            # LEAVE THE BROWSER NEUTRAL. Attach mode means this page OUTLIVES
            # the run -- the operator's own Chrome keeps whatever this left on
            # screen. The first run of this file did not do this and left an
            # open share menu behind, which is untidy rather than harmful and
            # is exactly the kind of thing that is never noticed until it is.
            # A navigation collapses it; nothing inside the menu is pressed.
            await BROWSER.goto(page, FEED_URL)
            print("    left the browser on the feed, menu collapsed.")
    except Exception as error:  # noqa: BLE001
        print(f"\nRUN ABORTED: {type(error).__name__}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
