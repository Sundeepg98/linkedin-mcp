"""Do this server's ADMITTED addresses stay admitted after LinkedIn redirects them?

THE QUESTION, AND IT WAS NOBODY'S. ``readonly.assert_read_url`` gates the
REQUESTED url and NEVER re-checks the LANDED one.
``tests/test_readonly_boundary_invariant.py`` has recorded that about
``/messaging/`` since August and calls it *"harmless today ... and a trap the
moment anyone adds that check."*

On 2026-09-05 a probe asked the shipped predicate about the address a browser
actually came to rest on, for ONE freshly admitted address, and it came back
REFUSED. That is one instance. **A register entry then claimed the check
generalises to the other patterns, and a claim about what a check WOULD find is
worth nothing beside a run of it.** So this runs it.

## WHAT IT SWEEPS, AND WHY THESE AND NOT THE WHOLE ALLOWLIST

Only addresses this server ALREADY LOADS in ordinary use -- the job-search
page, the three job-tracker stages and a posting view. Loading them adds no
exposure that the shipped tools do not already add every time they run.

**IT DOES NOT SWEEP THE WHOLE ALLOWLIST**, deliberately. Several admitted
addresses are pages nobody has opened, or are expensive, or belong to another
wave's surface; walking them at the end of a window to make a number bigger is
how a sweep becomes a cost nobody sanctioned. The bounded answer is the honest
one, and the file says which addresses it left alone.

## WHAT LEAVES THIS PROCESS

Per address: a LABEL typed into this file, the RELATION from ``_relation``, and
two BOOLEANS printed as literal branches -- did the landed PATH keep the asked
path, and does the shipped predicate admit the landed address. No url is
printed and none is derived into an output.

## THE CONTROL

The job-search page is read first and must come back admitted-after-landing. An
instrument that reported every address as refused-after-landing would look like
a discovery and be a bug, which is exactly the failure this repository has
already paid for twice today in a sibling probe.

## IT FIRES NO WRITE

It navigates and reads. No control is clicked and nothing is submitted.

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_landed_address_sweep.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from _probe_groups_events_live import _relation  # noqa: E402

#: (label, url). Every one is on the allowlist today and every one is loaded by
#: a shipped tool in ordinary use. The first is the CONTROL.
SWEEP: tuple[tuple[str, str], ...] = (
    ("CONTROL  the job search page",
     "https://www.linkedin.com/jobs/search/?keywords=node.js"),
    ("the tracker, saved stage",
     "https://www.linkedin.com/jobs-tracker/?stage=saved"),
    ("the tracker, applied stage",
     "https://www.linkedin.com/jobs-tracker/?stage=applied"),
    ("the tracker, draft stage (In Progress)",
     "https://www.linkedin.com/jobs-tracker/?stage=draft"),
    ("the recommended collection",
     "https://www.linkedin.com/jobs/collections/recommended"),
)


async def _sweep_one(page, label: str, url: str) -> bool:
    """Returns True when the landing is still admitted."""
    print(f"\n--- {label}")
    if not readonly.is_read_url(url):
        print("    NOT ADMITTED AT THE REQUEST. Nothing loaded, and this is a")
        print("    finding about the sweep list rather than about LinkedIn.")
        return False
    landed = await BROWSER.goto(page, url)
    relation = _relation(landed, url)
    kept = urlsplit(str(landed)).path.startswith(urlsplit(url).path.rstrip("/"))
    landed_admitted = readonly.is_read_url(str(landed))
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    print(f"    relation: {relation}")
    if walled:
        print("    AUTH WALL. This row measures the session, not the boundary.")
        return False
    if kept:
        print("    landed PATH still begins with the asked path: yes")
    else:
        print("    landed PATH still begins with the asked path: NO")
    if landed_admitted:
        print("    the LANDED address is admitted: yes")
    else:
        print("    the LANDED address is admitted: NO -- the server has come to")
        print("    rest where its own allowlist refuses")
    return landed_admitted


async def main() -> int:
    print("=== DO ADMITTED ADDRESSES STAY ADMITTED AFTER THE REDIRECT?")
    print("    Only addresses shipped tools already load. No write is fired.")

    _own_page = None
    refused_after_landing = 0
    measured = 0
    try:
        async with BROWSER.session() as page:
            _own_page = page
            for index, (label, url) in enumerate(SWEEP):
                ok = await _sweep_one(page, label, url)
                if index == 0:
                    if not ok:
                        print("\nCONTROL FAILED: a page that certainly serves came")
                        print("back refused after landing. NO MEASUREMENT TAKEN.")
                        return 1
                    continue
                measured += 1
                if not ok:
                    refused_after_landing += 1
    except Exception as error:  # noqa: BLE001
        name = type(error).__name__
        print(f"\nRUN ABORTED: {name}")
        if "ProfileLocked" in name:
            print("    The Chrome profile is held by another process. The")
            print("    cross-process guard working, not a defect.")
        else:
            print(f"    {error}")
        return 1
    finally:
        # THE PAGE, NEVER THE CONTEXT. The context is his signed-in browser.
        if _own_page is not None and not _own_page.is_closed():
            await _own_page.close()

    print("\n=== RESULT")
    print(f"    addresses measured beside the control : {measured}")
    print(f"    refused AFTER landing                 : {refused_after_landing}")
    if refused_after_landing == 0:
        print("    Every one of these stays inside the boundary it was admitted")
        print("    under. That BOUNDS the finding rather than reproducing it:")
        print("    the alerts case is not a general property of this allowlist.")
    else:
        print("    A SECOND CLASS OF INSTANCE. The alerts case is not alone, and")
        print("    the landed-url gap is worth closing rather than noting.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
