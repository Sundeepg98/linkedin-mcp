"""Does `/analytics/profile-views/` GAIN A CONTROL while it settles? NO PRESS.

## THE AMBIGUITY THIS RESOLVES, AND WHY IT NEEDS NO PRESS AT ALL

The second sanctioned press (2026-09-21, wave `what-is-reachable-now`) came
back with its witness reading ``disclosed: true`` for the first time -- and
with CLOSURE REFUSED:

    PAGE STATE BEFORE: expanded_true=0  expanded_false=8  dialogs=0  shape_total=8
    PAGE STATE AFTER : expanded_true=0  expanded_false=9  dialogs=0  shape_total=9
    CLOSURE -- page left as found: NO   {'expanded_false': (8, 9), 'shape_total': (8, 9)}

Two readings fit that equally and they have opposite consequences:

* **THE PRESS LEFT SOMETHING BEHIND.** A control appeared because of what the
  press did, and the closure condition is reporting a real residue.
* **THE PAGE WAS STILL DRAWING.** The before-reading was taken at
  ``shape_total=8`` on a page a 2026-09-19 capture measured at **9**, so the
  page may simply have finished hydrating between the two readings and the
  press is innocent.

``expanded_true`` is 0 and ``dialogs`` is 0 at BOTH ends, so nothing is left
OPEN either way -- the question is only whether the press is what changed the
count. **The gate cannot tell these apart and correctly refused to certify.**

**AND THE DISCRIMINATOR INVOLVES NO PRESS.** If the count drifts 8 -> 9 on a
page nobody touches, the press is exonerated by a measurement that costs
nothing and risks nothing. So this file loads the page and reads the same
shape counts three times, several seconds apart, **and presses nothing.**

## WHAT IT MAY NOT DO, STATED SO THE FILE CAN BE AUDITED AGAINST IT

**NO CLICK. NO KEYBOARD. NO FILL. NO SCROLL. NO PRESS.** This probe exists
precisely because the question can be answered without one, and a probe that
reached for a press here would be manufacturing the state it came to observe.
It calls exactly two things on the page: ``goto`` (via the shipped browser
helper) and ``locator(...).count()``.

**THE SELECTORS AND THE STATE READER ARE THE PRESS PROBE'S OWN**, imported
rather than copied, so a count here is comparable to a count there character
for character. A second implementation of a measurement whose whole purpose is
to be compared against the first would be measuring two things.

**WHAT LEAVES THIS PROCESS: integers.** No url, no page text, no name. The
address is a module constant in the shipped package and is never printed.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_analytics_settles_without_a_press.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

import _probe_first_sanctioned_press as presser  # noqa: E402

#: Seconds between readings. The press run's two readings were separated by
#: the press, the Escape and two attribute reads -- a few seconds. These
#: bracket that.
WAITS = (0.0, 4.0, 8.0)


async def main() -> int:
    if not os.environ.get("LINKEDIN_CDP_ATTACH"):
        print("REFUSING: LINKEDIN_CDP_ATTACH is not set. This probe attaches")
        print("to the browser already running on the persistent profile and")
        print("never launches one.")
        return 1

    url = presser.TARGET_URL
    print("=" * 70)
    print("DOES THE ANALYTICS PAGE SETTLE UPWARDS ON ITS OWN? NO PRESS TAKEN.")
    print("=" * 70)
    print("\n  address admitted (checked before any load): "
          + str(readonly.is_read_url(url)))
    if not readonly.is_read_url(url):
        print("  REFUSING: the address is not admitted.")
        return 1

    readings = []
    try:
        async with BROWSER.session() as page:
            await BROWSER.goto(page, url)
            for index, wait in enumerate(WAITS):
                if wait:
                    await asyncio.sleep(wait)
                state = await presser._page_state(
                    page, "READING " + str(index + 1)
                    + " (t+" + str(int(wait)) + "s, NOTHING PRESSED)")
                readings.append(state)
    except Exception as exc:  # noqa: BLE001 - TYPE only, never the message
        print("\n  THE RUN RAISED " + type(exc).__name__
              + " -- message deliberately not printed")
        return 1
    finally:
        try:
            own = getattr(BROWSER, "_own_page", None)
            if own is not None and not own.is_closed():
                # BOUND TO `page` ON PURPOSE -- the tab-leak ratchet in
                # `tests/test_a_probe_closes_its_own_tab.py` recognises a
                # close by NAME, so a clean probe using any other variable
                # reads as a leak and pushes a pin that may only go down.
                page = own
                await page.close()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    closing our tab raised " + type(exc).__name__)
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    cleanup raised " + type(exc).__name__)

    print("\n" + "=" * 70)
    print("### THE ANSWER")
    keys = ("expanded_true", "expanded_false", "dialogs", "shape_total")
    moved = {}
    for key in keys:
        series = [r.get(key) for r in readings]
        print("    " + key.ljust(16) + " -> ".join(str(v) for v in series))
        if len({v for v in series if v is not None}) > 1:
            moved[key] = series

    if moved:
        print("\n    THE PAGE MOVES ON ITS OWN. These counts changed with")
        print("    NOTHING PRESSED: " + ", ".join(sorted(moved)))
        print("    A closure check that compares one reading taken while the")
        print("    page is still drawing against one taken after it has")
        print("    settled will report a difference the press did not cause.")
        return 0

    print("\n    THE PAGE DID NOT MOVE across " + str(len(WAITS))
          + " readings with nothing pressed.")
    print("    So the 8 -> 9 seen across the press is NOT explained by late")
    print("    hydration on this evidence, and the closure refusal stands as")
    print("    a finding about the press rather than about the clock.")
    print("    NOTE THE BOUND: this run began from a fresh load. If the page")
    print("    had already settled before READING 1, a real early-draw window")
    print("    would be invisible here -- absence of drift after the settle")
    print("    is not absence of drift before it.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
