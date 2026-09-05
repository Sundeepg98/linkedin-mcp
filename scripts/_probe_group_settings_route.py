"""Where does `Update your settings` go, and would the boundary let us follow?

TWO CENSUS ROWS HANG ON THIS. `N 170` ("allow or prevent other group members
from messaging you") and `N 176` ("prevent your network being updated when you
join a group") are both per-group SETTINGS, and `_probe_groups_menu.py`
measured that every membership row draws an `Update your settings` control --
five of them, twice each, on an address this server may already open.

**BUT A CONTROL BEING DRAWN IS NOT A ROUTE.** If it navigates to a per-group
settings address, `settings` and `/settings/` are BOTH on
`_FORBIDDEN_URL_SUBSTRINGS` and are checked BEFORE the allowlist -- so those
two rows would be DOUBLE-refused exactly as `/groups/<id>/invite/` is, and
would need a denylist exemption, which is a heavier act than an allowlist
addition. If it opens a modal on the same page instead, they cost nothing at
all.

## IT DOES NOT PRESS AND IT DOES NOT NAVIGATE

The question is answered from the HREF, classified against the two gates
independently -- which is `scripts/_probe_retire_ruling_boundary.py`'s method,
applied one surface along:

    FORBIDDEN xN   N substrings somebody wrote, each with an argument beside it
    NO-PATTERN     the default-closed allowlist, which decided nothing
    ALLOWED        an existing pattern already admits it

**A VERDICT OF "REFUSED" CANNOT TELL THOSE APART AND THE CLASS CAN**, which is
the whole point: this repository's own rule is that a general mechanism which
merely happens to block something is a GAP WITH A NAMED BLOCKER and may not be
laundered into a decision.

A control with NO href is its own answer, and a better one: it is a button, so
it opens something in place and no boundary is involved.

## NO ADDRESS IS PRINTED. NOT ONE.

What is emitted per control: whether it has an href at all, the number of PATH
SEGMENTS, which forbidden substrings matched (this repository's own vocabulary,
naming nobody), and the allowlist verdict. **Never the href, never a segment,
never a fragment of either.** A group id is his own data but this is a
transcript, and the rule this project keeps is that the caller decides what it
says.

## AIMED BY A LABEL, AND THE LABEL IS FURNITURE

`Update your settings` was measured at count 5 across five rows and count 10
across five menus, so it is furniture by the same tally rule that redacts a
name -- which is why it is safe to write into a tracked file and safe to match
on. A label appearing once would be a name and would not be here.

Usage::

    LINKEDIN_CDP_ATTACH_TIMEOUT_MS=60000 LINKEDIN_CDP_ATTACH=1 \\
        LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_group_settings_route.py
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

#: FURNITURE, not a name. Measured at 5 across the rows and 10 across the
#: menus, so the tally rule that redacts a singleton keeps this one.
SETTINGS_LABEL = "Update your settings"

#: The control's href, read from the page. Returns hrefs and counts; the hrefs
#: are classified in Python and never printed.
LINKS_JS = """
(cfg) => {
  const nodes = Array.from(
    document.querySelectorAll('a[href], button')
  ).filter((n) => {
    const label = (n.getAttribute('aria-label') || n.textContent || '').trim();
    return label === cfg.label;
  });
  return {
    matched: nodes.length,
    tags: nodes.map((n) => n.tagName),
    hrefs: nodes.map((n) => n.getAttribute('href')),
  };
}
"""


def _classify(href):
    """The two gates, asked INDEPENDENTLY. Returns a class and counts only."""
    if not href:
        return {"has_href": False, "class": "NO HREF -- opens in place"}
    absolute = href if href.startswith("http") else f"{BASE_URL}{href}"
    hits = [
        needle
        for needle in readonly._FORBIDDEN_URL_SUBSTRINGS
        if needle in absolute
    ]
    allowed = readonly.is_read_url(absolute)
    segments = len([s for s in absolute.split("://")[-1].split("/")[1:] if s])
    if allowed:
        verdict = "ALLOWED by an existing pattern"
    elif hits:
        verdict = f"FORBIDDEN x{len(hits)}: {sorted(hits)}"
    else:
        verdict = "NO-PATTERN -- the default-closed allowlist, no substring"
    return {
        "has_href": True,
        "path_segments": segments,
        "class": verdict,
        "forbidden_hits": len(hits),
    }


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set. A launch-mode session "
              "would open a SECOND Chrome on the operator's own profile.")
        return 2
    if not readonly.is_read_url(GROUPS_URL):
        print("REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    print("=== WHERE DOES 'Update your settings' GO?")
    print("    Nothing is pressed and nothing is navigated. NO ADDRESS IS "
          "PRINTED -- only the class and the counts.")

    page_ref = None
    reading = {}
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
                LINKS_JS, {"label": SETTINGS_LABEL}
            )
            await BROWSER.goto(page, FEED_URL)
            after = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )
            print(f"    badge on the feed AFTER: {after.get('state')} "
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
    finally:
        # CLOSE THE TAB THIS RUN OPENED -- see the sibling probes. Attach mode
        # opens one per run and never closes it.
        if page_ref is not None and not page_ref.is_closed():
            await page_ref.close()

    matched = int(reading.get("matched") or 0)
    print(f"\n=== CONTROLS WEARING THAT LABEL: {matched}")
    if matched == 0:
        print("    ZERO. The label was measured at 5 on this page an hour "
              "ago, so this is a finding about this match rule or about a "
              "changed page -- and NOT a finding that the control is gone.")
        return 1

    tags = {}
    for tag in (reading.get("tags") or []):
        tags[str(tag)] = tags.get(str(tag), 0) + 1
    print(f"    by tag: {tags}")

    verdicts = {}
    for href in (reading.get("hrefs") or []):
        row = _classify(href)
        key = f"{row['class']}  [segments {row.get('path_segments', 0)}]"
        verdicts[key] = verdicts.get(key, 0) + 1
    print("    CLASS PER CONTROL:")
    for key, count in sorted(verdicts.items(), key=lambda i: (-i[1], i[0])):
        print(f"        {count:>3}  {key}")

    print("\n=== WHAT THIS SETTLES")
    if all(not href for href in (reading.get("hrefs") or [])):
        print("    EVERY control opens IN PLACE -- no href, so no address and "
              "no boundary question. N 170 and N 176 cost no boundary change; "
              "what they need is a press and a reader.")
    elif any(_classify(h).get("forbidden_hits") for h in (reading.get("hrefs") or [])):
        print("    At least one control navigates to an address meeting a "
              "FORBIDDEN SUBSTRING. N 170 and N 176 are DOUBLE-refused, the "
              "way /groups/<id>/invite/ is, and need a denylist exemption "
              "rather than an allowlist addition.")
    else:
        print("    The controls navigate and meet NO written substring, so "
              "the default-closed allowlist is what refuses them. That is a "
              "GAP WITH A NAMED BLOCKER and not a decision anybody made.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
