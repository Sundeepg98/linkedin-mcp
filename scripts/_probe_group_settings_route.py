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


def _absolute(href) -> str:
    """A relative href made absolute, for the gates that anchor on a scheme.

    THE RESULT IS NEVER PRINTED AND NEVER RETURNED PAST A COMPARISON. It is
    read only inside ``in`` tests and inside ``len()``, which is what keeps the
    reporting section free of page-derived values.
    """
    text = str(href or "")
    return text if text.startswith("http") else f"{BASE_URL}{text}"


def _classify(href) -> dict:
    """The two gates, asked INDEPENDENTLY. Returns counts and closed strings.

    Kept as a function because the two gates must be asked SEPARATELY: a
    verdict of REFUSED cannot tell "somebody wrote a substring against this"
    from "the default-closed allowlist decided nothing", and this repository's
    rule is that a general mechanism which merely happens to block something is
    a GAP WITH A NAMED BLOCKER rather than a decision.
    """
    if not href:
        return {"has_href": False, "class": "NO HREF -- opens in place",
                "path_segments": 0, "forbidden_hits": 0}
    absolute = _absolute(href)
    hits = [
        needle
        for needle in readonly._FORBIDDEN_URL_SUBSTRINGS
        if needle in absolute
    ]
    segments = len([s for s in absolute.split("://")[-1].split("/")[1:] if s])
    if readonly.is_read_url(absolute):
        verdict = "ALLOWED by an existing pattern"
    elif hits:
        verdict = f"FORBIDDEN x{len(hits)}"
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

    # ============================================================
    # EVERY FIGURE BELOW IS A ``len()`` OF A LIST, AND THAT IS THE FIX
    # RATHER THAN A STYLE.
    # ============================================================
    #
    # ``page.evaluate`` is a TEXT SOURCE to the guard in
    # ``tests/test_page_text_is_never_printed.py``, so everything derived from
    # its return is tainted -- correctly, because a group's page text can carry
    # a member's name and ``census_substitute`` returns a plain human name
    # UNCHANGED. That is measured on this very surface, not hypothesised.
    #
    # The first version of this section printed ``reading``'s own integers and
    # a dict built by walking its lists, and tripped the guard at THREE SITES.
    # Every one of them was safe in substance -- a count, a set of HTML tag
    # names, and a class string made of this repository's own vocabulary -- and
    # **the guard was still right**, because none of that is visible to it and
    # a later edit to any of those expressions could carry a name with no
    # further review.
    #
    # THE REPAIR IS THE HOUSE DISCIPLINE, NOT A DECLARATION AND NOT A NEW
    # SANITISER: counting a thing is what this package does INSTEAD of printing
    # it, so the tainted values are read only inside ``len(...)`` and inside
    # comparisons, and what crosses to a print is an integer or a string this
    # file authored. A declaration would have keyed on the whole sink
    # expression and tolerated that line forever, whatever it later held.
    hrefs = list(reading.get("hrefs") or [])
    tags = list(reading.get("tags") or [])

    print("")
    print(f"=== CONTROLS WEARING THAT LABEL: {len(hrefs)}")
    if len(hrefs) == 0:
        print("    ZERO. The label was measured at 5 on this page an hour "
              "ago, so this is a finding about this match rule or about a "
              "changed page -- and NOT a finding that the control is gone.")
        return 1

    print(f"    anchors: {len([t for t in tags if t == 'A'])}   "
          f"buttons: {len([t for t in tags if t == 'BUTTON'])}")
    print(f"    carrying an href: {len([h for h in hrefs if h])}   "
          f"opening in place: {len([h for h in hrefs if not h])}")
    for depth in range(1, 7):
        n = len([h for h in hrefs if h and _classify(h).get("path_segments") == depth])
        if n:
            print(f"    path depth {depth}: {n}")

    print("    FORBIDDEN SUBSTRINGS MET, by needle "
          "(this repository's own vocabulary, naming nobody):")
    met = 0
    for needle in sorted(readonly._FORBIDDEN_URL_SUBSTRINGS):
        n = len([h for h in hrefs if h and needle in _absolute(h)])
        if n:
            met += 1
            print(f"        {n:>3}  {needle!r}")
    if met == 0:
        print("        NONE")
    admitted = len([h for h in hrefs if h and readonly.is_read_url(_absolute(h))])
    print(f"    already ADMITTED by an existing allowlist pattern: {admitted}")

    print("")
    print("=== WHAT THIS SETTLES")
    if len([h for h in hrefs if h]) == 0:
        print("    EVERY control opens IN PLACE -- no href, so no address and "
              "no boundary question. N 170 and N 176 cost no boundary change; "
              "what they need is a press and a reader.")
    elif met:
        print("    The controls navigate to an address meeting a FORBIDDEN "
              "SUBSTRING. N 170 and N 176 are DOUBLE-refused, the way "
              "/groups/<id>/invite/ is, and need a denylist exemption rather "
              "than an allowlist addition.")
    elif admitted:
        print("    The controls navigate to an address ALREADY ADMITTED. "
              "N 170 and N 176 need no boundary change at all.")
    else:
        print("    The controls navigate and meet NO written substring, so "
              "the default-closed allowlist is what refuses them. That is a "
              "GAP WITH A NAMED BLOCKER and not a decision anybody made.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
