"""THE FIRST SANCTIONED PRESS. The gate decides; this file only supplies it.

Authorised for `N 133` / `N 134` on `/analytics/profile-views/`. **The
authorisation is for the MECHANISM to be used as designed, not for a press.**
This file does not decide to press. It evaluates through ``press.disclose`` and
that function decides. If it refuses -- including on
``no_counter_prices_this_press``, which this wave flagged as an open question
for this page -- **the refusal is recorded and the run stops.** A refusal here
is a real result and is worth more than a press taken around it.

## Why this page and not the open-to-work controls

`/analytics/profile-views/` is his own data with no outward-facing setting
attached. The `open_to` controls sit beside a value recruiters see; an expand
there is still a render, but it is one keystroke from a surface that presents
him to other people. The first press should not be adjacent to that.

## What this file supplies, and the one judgement in it

``press.disclose`` requires a ``read_counters`` callable. **The judgement is
WHICH counters, and it is made here rather than by the gate**, so it is stated
plainly:

    read_invitation_badge      dom.py       pending invitations
    read_notifications_badge   notify_cost  unread notifications

Both are the repository's established cost instruments and both are documented
to render on the nav of any signed-in page. **Both are also built to REFUSE
rather than report a false zero** -- every early return leaves the label at
None -- which is exactly what condition 3 needs, because an unreadable counter
is not a zero and `check_counters` refuses on one.

**EVERY COUNTER ATTEMPTED IS REPORTED, INCLUDING AS None.** Silently omitting
one that could not be read would turn "I could not price this press" into "no
such counter exists", which are different claims and only the first is true.

## What this file will NOT do

* It presses nothing itself. ``disclose`` performs the one click.
* It presses nothing the gate did not evaluate, including to check something
  adjacent.
* It does not retry. If anything is unexpected -- a control that moves, a count
  that changes, a page that does not return to its prior state -- it stops and
  reports. There is no version of this where pressing twice is better than
  reporting once.

Run::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        LINKEDIN_CDP_ATTACH_TIMEOUT_MS=60000 \\
        ./venv/Scripts/python.exe scripts/_probe_first_sanctioned_press.py

Writes NOTHING. Prints to stdout.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, dom, notify_cost, press, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

TARGET_URL = f"{BASE_URL}/analytics/profile-views/"
SHAPE = "[aria-expanded]"


def _as_int(value):
    """An int, or None. NEVER a zero standing in for an unread counter."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else None


async def make_counter_reader(page):
    async def read_counters():
        out = {}
        try:
            inv = await dom.read_invitation_badge(page)
            out["invitations"] = _as_int(
                inv.get("label") if isinstance(inv, dict) else None
            )
        except Exception as exc:  # noqa: BLE001
            print(f"    invitation badge raised {type(exc).__name__}")
            out["invitations"] = None
        try:
            note = await notify_cost.read_notifications_badge(page)
            if isinstance(note, dict):
                value = note.get("unread")
                if value is None:
                    value = note.get("label")
                out["notifications_unread"] = _as_int(value)
            else:
                out["notifications_unread"] = None
        except Exception as exc:  # noqa: BLE001
            print(f"    notifications badge raised {type(exc).__name__}")
            out["notifications_unread"] = None
        return out

    return read_counters


async def _page_state(page, when: str) -> dict:
    """Enough to say the page was left as found, without printing a url."""
    state = {}
    try:
        landed = str(getattr(page, "url", "") or "")
        state["url_relation"] = (
            "target" if landed.rstrip("/") == TARGET_URL.rstrip("/")
            else "MOVED"
        )
        state["expanded_true"] = await page.locator(
            '[aria-expanded="true"]'
        ).count()
        state["expanded_false"] = await page.locator(
            '[aria-expanded="false"]'
        ).count()
        state["dialogs"] = await page.locator('[role="dialog"]').count()
        state["shape_total"] = await page.locator(SHAPE).count()
    except Exception as exc:  # noqa: BLE001
        state["error"] = type(exc).__name__
    print(f"    PAGE STATE {when}: " + "  ".join(
        f"{k}={v}" for k, v in state.items()
    ))
    return state


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        return 2

    print("=" * 72)
    print("THE FIRST SANCTIONED PRESS -- the gate decides, this file supplies")
    print("=" * 72)

    # CONDITION 1, CHECKED BEFORE ANYTHING IS OPENED.
    print("\n  CONDITION 1 -- address admitted, checked before any load:")
    print(f"      readonly.is_read_url : {readonly.is_read_url(TARGET_URL)}")
    print(f"      press.check_address  : {press.check_address(TARGET_URL)}")
    if not readonly.is_read_url(TARGET_URL):
        print("      REFUSED. Nothing is loaded.")
        return 2

    # CONDITION 2, ON THE SHAPE KEY, BEFORE ANYTHING IS OPENED.
    print("\n  CONDITION 2 -- shape is an enumerated key, not a selector:")
    print(f"      sanctioned shapes    : {press.SANCTIONED_SHAPES}")
    print(f"      press.check_shape    : {press.check_shape(SHAPE)}")
    if press.check_shape(SHAPE).get("refused"):
        print("      REFUSED. Nothing is loaded.")
        return 2

    page = None
    try:
        async with BROWSER.session() as opened:
            page = opened
            landed = await BROWSER.goto(page, TARGET_URL)
            if "/login" in str(landed) or "/checkpoint" in str(landed):
                print("\n  AUTH WALL. Nothing here is a reading. Stopping.")
                return 1
            try:
                await page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception as exc:  # noqa: BLE001
                print(f"    settle wait: {type(exc).__name__}")

            print()
            before_state = await _page_state(page, "BEFORE")

            reader = await make_counter_reader(page)
            print("\n  COUNTER READING, taken on the page already open:")
            probe = await reader()
            for name, value in sorted(probe.items()):
                print(f"      {name:22s} {value}")
            print("      (None means UNREAD, never zero. check_counters "
                  "refuses on an unreadable counter.)")

            print("\n  HANDING TO press.disclose. It decides from here.")
            verdict = await press.disclose(
                page, shape=SHAPE, index=0, read_counters=reader
            )
            print("\n  VERDICT, verbatim:")
            print("      " + json.dumps(verdict, sort_keys=True))

            if verdict.get("refused"):
                print(f"\n  REFUSED: {verdict.get('refused')}")
                print(f"      why  : {verdict.get('why')}")
                print(f"      reachable_by_this_route: "
                      f"{verdict.get('reachable_by_this_route')}")
                print("      RECORDED AND STOPPING. A refusal here is a real "
                      "result; it is not retried and nothing is pressed "
                      "around it.")
            else:
                print("\n  PERMITTED. The press was taken by the gate.")
                print(f"      priced_by: {verdict.get('priced_by')}")

            print()
            after_state = await _page_state(page, "AFTER ")
            same = {
                key: (before_state.get(key), after_state.get(key))
                for key in sorted(set(before_state) | set(after_state))
                if before_state.get(key) != after_state.get(key)
            }
            print(f"\n  CLOSURE -- page left as found: "
                  f"{'YES' if not same else 'NO'}")
            if same:
                print(f"      DIFFERENCES: {same}")
                print("      STOPPING. The page did not return to its prior "
                      "state and that is reported rather than retried.")
    finally:
        if page is not None:
            try:
                await page.close()
                print("\n    page closed.")
            except Exception as exc:  # noqa: BLE001
                print(f"\n    page close failed: {type(exc).__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
