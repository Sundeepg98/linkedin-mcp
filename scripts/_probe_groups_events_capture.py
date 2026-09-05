"""What separates a membership row from a recommendation row?

THE PRECONDITION IS HALF ANSWERED AND THIS IS THE OTHER HALF.
``_probe_groups_events_live.py`` established, with a control passing at both
ends of the session and two agreeing readings per surface, that the two roots
SERVE and draw entity links: 10 group-marked hrefs and 54 event-marked hrefs.
**He is not at zero.** What that does NOT establish is how many are HIS -- both
roots draw recommendations alongside his own, and both are entity links, so a
count of group hrefs is not a count of memberships.

That is the question this file exists for, and it asks it the cheap way first.

## TWO OUTPUTS, AND ONLY ONE OF THEM IS SEEN

**THE REPORT is entirely shaped.** Every figure printed comes from
``dom.read_surface_census``, which reduces each name and href to a shape inside
itself and REDACTS the name beside any control pointing at a named entity.
Nothing raw is printed, echoed, or summarised. The discriminator it looks for
is the CONTAINER: if his own groups and LinkedIn's suggestions sit in different
containers, the container shapes differ and the split falls out with no name
ever crossing.

**THE CAPTURE is raw and goes to one gitignored path.** ``_audit/_probe-*.html``
is matched by ``.gitignore:140`` -- verified before this file was written, not
assumed -- so the page cannot reach a commit from there. It exists because a
future membership READER needs a fixture and no document in this repository has
ever held a group or event surface. **It is written and NOT read back by this
script.** Sanitising it is a separate, deliberate step with its own gates.

## THE SANITISATION TRAP, NAMED HERE BECAUSE THIS IS WHERE IT WILL BITE

Whoever turns that capture into a fixture must run the RED/GREEN pair rather
than reasoning about it. Adding a substitution WITHOUT its placeholder yields
``<opaque>`` everywhere -- **a redaction with no marker, which is worse than
the leak**, because ``census_href_identifies_entity`` returns False on it and
the name beside it ships. That mistake is documented on
``shape._CENSUS_PLACEHOLDER`` and has now caught two waves on two days,
including the author of this file, one day after reading the note. Reading it
prevented nothing; running the pair caught it in a minute.

## ATTACH MODE ONLY

Chrome runs externally on the operator's real profile and the server ATTACHES
rather than launching. ``LINKEDIN_CDP_ATTACH=1`` is asserted below and this
script REFUSES to run without it: a launch-mode session would open a second
Chrome on the same profile, which is the exact failure the transport cutover
exists to end.

Usage::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_groups_events_capture.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: The gitignored capture directory. ``.gitignore:140`` matches
#: ``*_probe-*.html``, so a file named this way cannot be committed.
OUT = ROOT / "_audit"

SURFACES = (
    ("groups", f"{BASE_URL}/groups/", "/groups/<group>"),
    ("events", f"{BASE_URL}/events/", "/events/<event>"),
)

#: The control, and it is the same one the sibling probe uses: 20 controls on
#: six readings across two days and three builds. If it does not read about 20,
#: nothing else in the run is a reading.
CONTROL_URL = f"{BASE_URL}/mypreferences/d/dark-mode"
CONTROL_EXPECTED = 20


def _relation(landed: str, asked: str) -> str:
    """The RELATION between two addresses, carrying neither of them.

    Byte-identical in contract to the function of the same name in
    ``_probe_groups_events_live.py``, and declared once for both in
    ``tests/test_navigation_is_never_derived.py::_SANITISERS``. Every branch
    returns a literal or an integer path depth; no substring of either input
    can survive. The proof is a test, not this sentence -- an entry on that
    list is a claim about a function's contract, and this repository has
    already admitted one function there on the strength of its NAME and found
    it had no rule at all.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


async def _capture(page, name: str, url: str, marker: str) -> dict:
    print(f"\n--- {name.upper()}  {url}")
    if not readonly.is_read_url(url):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return {"refused": True}

    landed = await BROWSER.goto(page, url)
    # THE RELATION, NEVER THE URL. _relation is declared in
    # tests/test_navigation_is_never_derived.py::_SANITISERS and its contract
    # -- that nothing of either input survives into the result -- is PROVEN
    # there rather than promised here.
    relation = _relation(landed, url)
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    print(f"    relation: {relation}")
    if walled:
        print("    AUTH WALL. Nothing else measured, nothing captured.")
        return {"authwall": True}

    census = await dom.read_surface_census(page)
    controls = list(census.get("controls") or [])
    read = int(census.get("controls_read") or 0)
    marked = [
        row for row in controls
        if marker in str(row.get("href_shape") or "")
    ]
    print(f"    controls_read={read}  {marker} hrefs={len(marked)}")

    # THE DISCRIMINATOR. Container shapes, tallied over the marked controls
    # only. If his own and LinkedIn's suggestions sit in different containers,
    # the split is visible here and no name is needed to see it.
    by_container: dict[str, int] = {}
    by_role: dict[str, int] = {}
    for row in marked:
        container = str(row.get("container") or "none")
        by_container[container] = by_container.get(container, 0) + 1
        role = f"{row.get('tag') or '?'}/{row.get('role') or 'none'}"
        by_role[role] = by_role.get(role, 0) + 1

    print(f"    CONTAINERS over the {len(marked)} marked controls "
          f"({len(by_container)} distinct):")
    for container, count in sorted(
        by_container.items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"        {count:>3}  {container}")
    print("    TAG/ROLE:")
    for role, count in sorted(
        by_role.items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"        {count:>3}  {role}")

    # THE CAPTURE. Written, never read back here, never printed from.
    html = await page.content()
    target = OUT / f"_probe-{name}-hyd.html"
    target.write_text(html, encoding="utf-8")
    print(f"    captured {len(html)} chars -> {target.name} (gitignored)")
    return {
        "controls": read,
        "marked": len(marked),
        "containers": len(by_container),
        "chars": len(html),
    }


async def main() -> int:
    # ATTACH MODE IS A PRECONDITION, NOT A PREFERENCE. A launch-mode session
    # would open a second Chrome on the operator's real profile.
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print("    Chrome is running externally on the operator's own profile "
              "and this script attaches to it. Starting a launch-mode session "
              "would open a SECOND Chrome on that profile, which is the "
              "failure the transport cutover exists to end.")
        print(f"    Re-run with LINKEDIN_CDP_ATTACH=1 "
              f"LINKEDIN_CDP_PORT={config.CDP_PORT}")
        return 2

    print("=== GROUPS AND EVENTS: WHAT SEPARATES HIS OWN FROM A SUGGESTION?")
    print(f"    attach mode, port {config.CDP_PORT}. Report is SHAPED; the "
          "capture is raw and gitignored.")

    page_ref = None
    try:
        async with BROWSER.session() as page:
            page_ref = page
            print("\n### CONTROL FIRST.")
            control = await _capture(
                page, "control-darkmode", CONTROL_URL, "/never/<match>"
            )
            results = {}
            for name, url, marker in SURFACES:
                results[name] = await _capture(page, name, url, marker)
    except Exception as error:  # noqa: BLE001
        print(f"\nRUN ABORTED: {type(error).__name__}: {error}")
        return 1
    # CLOSE THE TAB THIS RUN OPENED. Measured 2026-09-05: in ATTACH mode
    # ``BROWSER._page()`` calls ``ctx.new_page()`` AND CACHES IT, and
    # ``session()``'s own ``finally`` only touches an idle timer -- so the tab
    # OUTLIVES THE PROCESS. One leaked tab per probe run, in the operator's own
    # Chrome. Across the fleet: 42 scripts call ``session()`` and 5 closed
    # their page; 27 tabs and 125 CDP targets had accumulated, and
    # ``connect_over_cdp`` enumerates every target during the handshake, which
    # is what put every wave's live work on a coin flip against a 15s ceiling.
    #
    # THE PAGE, NEVER THE CONTEXT. The context is his signed-in browser
    # session; closing it closes his window.
    #
    # AND NOT IN ``browser.py``, which is a ruling for whoever owns it rather
    # than a drive-by: ``session()`` is shared by every server tool, and those
    # legitimately REUSE the cached page across calls, so a per-session close
    # there would churn tabs for a different caller. A probe is a one-shot and
    # has nothing to keep.
    #
    # In a ``finally``, because the runs that ABORT are exactly the ones that
    # were leaking.
    finally:
        if page_ref is not None and not page_ref.is_closed():
            await page_ref.close()

    print("\n=== CONTROL")
    if control.get("refused") or control.get("authwall"):
        print("  NOT READ. Nothing else in this run is a reading.")
        return 1
    read = int(control["controls"])
    floor = int(CONTROL_EXPECTED * 0.5)
    ok = read >= floor
    print(f"  read {read}, expected about {CONTROL_EXPECTED}, floor {floor} "
          f"-- {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  FAILED, so every count above is a reading about this run "
              "rather than about his account.")
        return 1

    print("\n=== THE DISCRIMINATION QUESTION")
    for name, _url, marker in SURFACES:
        row = results.get(name) or {}
        if row.get("refused") or row.get("authwall"):
            print(f"  {name}: NOT READ")
            continue
        marked, containers = int(row["marked"]), int(row["containers"])
        if marked == 0:
            print(f"  {name}: zero marked controls, so there is nothing to "
                  "separate. That contradicts the sibling probe and one of "
                  "the two readings is wrong -- do not interpret either.")
        elif containers <= 1:
            print(f"  {name}: {marked} marked controls in {containers} "
                  "container. **The container does NOT separate them**, so "
                  "this cheap route fails and the capture is what has to "
                  "answer it.")
        else:
            print(f"  {name}: {marked} marked controls across {containers} "
                  "distinct containers. A split EXISTS in the shapes -- read "
                  "the tallies above; the largest container is the candidate "
                  "for whichever class LinkedIn draws most of.")
    print("\n  WHICH CONTAINER IS 'HIS' IS NOT DECIDED HERE. A count per "
          "container is a structural fact; naming one of them as his "
          "memberships needs the capture, and that ruling is not this "
          "script's to make.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
