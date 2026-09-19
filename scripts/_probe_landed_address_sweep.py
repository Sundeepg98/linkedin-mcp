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

## THE RESULT, 2026-09-19, AND THE COUNT IS 3 OF 10

    refused after landing   /jobs/collections/recommended       (no slash)
                            /jobs/collections/recommended/      (with slash)
                            /in/me/
    admitted after landing  jobs search, three tracker stages,
                            premium, search appearances, groups, messaging

**SO IT IS A CLASS, NOT A CURIOSITY.** Three of ten admitted addresses come to
rest where this server's own allowlist would refuse them. The allowlist is
guaranteeing something about REQUESTS that does not hold for LANDINGS.

**AND THE PROFILE ROW COST TWO EXTRA PROBES, WHICH IS THE PART WORTH READING.**
This sweep read ``/in/me/`` as ADMITTED after landing. A standalone probe had
read it REFUSED, once. Rather than pick the reading that agreed with the sweep,
both were repeated:

    standalone, 3 rounds                    REFUSED 3 of 3
    cold / after jobs search / after feed   REFUSED 3 of 3
    this sweep, loaded 7th                  ADMITTED  1 of 1

**Six refusals against one admission, across two probes and three different
predecessor pages.** The warming hypothesis -- that a single-page app routes
``/in/me/`` client-side once it is hot, so only a cold load takes the server
redirect -- was tested directly and REFUTED: the predecessor makes no
difference. The one ADMITTED reading is unexplained and is the outlier.

**THE LESSON IS THE ONE THIS FILE ALREADY TEACHES, AIMED AT ITSELF: a sweep
row is a single reading.** Ten addresses measured once each is ten single
readings, and the one that disagreed with a sibling probe was the only one that
got repeated. The other nine were no better evidenced -- they simply had
nothing contradicting them yet.

## SECOND PASS, 2026-09-19, ORDER REVERSED -- and it settles the profile

Run again with ``--reverse``: the control stays first and every other row gets
a DIFFERENT PREDECESSOR than in pass one, so a row that agrees with itself has
agreed across two contexts rather than reproduced one sequence.

    nine rows            SAME VERDICT as pass one
    the profile          REFUSED this time, where pass one read ADMITTED

**So the profile is now REFUSED in 7 of 8 readings** across three probes and
four different predecessors, and pass one's ADMITTED stands alone and
unexplained. **The outlier was the sweep's own row**, which is the instrument
this file is -- and it took a repeat to find that, exactly as the paragraph
above predicted of itself.

One thing that moved without mattering: the CONTROL's relation differs between
passes while its admission does not. A relation is sensitive to query strings
and canonicalisation; the verdict is not. Worth knowing before anyone treats a
changed relation as a changed outcome.

## WHAT EACH REFUSAL ACTUALLY REFUSES ON

Reported as the RULE, never the url -- a landed address carrying a vanity slug
is precisely what the identity apparatus exists to keep out of files.

    /in/me/                          NO PATTERN MATCHES
    /jobs/collections/recommended    NO PATTERN MATCHES
    /jobs/collections/recommended/   NO PATTERN MATCHES

**NOT ONE OF THE THREE IS A FORBIDDEN SUBSTRING.** That distinction is the
whole of the ruling that follows, and it cuts against the natural reading:

* a FORBIDDEN SUBSTRING is a deliberate class ban, checked before the allowlist
  is consulted at all -- somebody decided;
* NO PATTERN MATCHING is **the absence of a permission, not the presence of a
  prohibition** -- nobody decided anything about this spelling.

So the landed profile is not refused *because a slug is a name*; there is no
rule to that effect. It is refused because the allowlist admits ``/in/me/`` and
nothing else under ``/in/``, and the canonical spelling LinkedIn redirects to
was never considered. This repository has a name for that: a GAP with a named
blocker, not a decision.

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
    # WIDENED 2026-09-19. /in/me/ was measured ADMITTED AT THE REQUEST AND
    # REFUSED AT THE LANDING while chasing an unrelated question, which turned
    # this from a two-instance curiosity into a class worth sizing. Every
    # address below is on the allowlist AND is opened by a shipped tool in
    # ordinary use, so the sweep still adds no exposure those tools do not.
    ("the recommended collection, WITH the trailing slash",
     "https://www.linkedin.com/jobs/collections/recommended/"),
    ("his own profile (my_activity_items, the intro readers)",
     "https://www.linkedin.com/in/me/"),
    ("premium entitlement (linkedin_premium_status)",
     "https://www.linkedin.com/premium/my-premium/"),
    ("search appearances (linkedin_search_appearances)",
     "https://www.linkedin.com/analytics/search-appearances/"),
    ("groups (groups_page.read_group_memberships)",
     "https://www.linkedin.com/groups/"),
    ("messaging (linkedin_open_messaging)",
     "https://www.linkedin.com/messaging/"),
)

#: LEFT ALONE DELIBERATELY, and the reason is a measurement rather than
#: caution. ``/notifications/`` is admitted and IS opened by a shipped tool --
#: and the census records one measured call on 2026-08-21 taking the badge from
#: 1 to 0, where it stayed. Loading it to ask a boundary question would consume
#: something to learn where a redirect goes. ``/feed/`` is omitted for the
#: opposite reason: it was read four times today and serves EXACT every time,
#: so a fifth load buys nothing.
NOT_SWEPT: tuple[tuple[str, str], ...] = (
    ("/notifications/", "loading it consumes the invitation badge"),
    ("/feed/", "already measured SERVED exact four times today"),
)


def _why_refused(url: str) -> str:
    """WHICH RULE refuses this address -- reported as the rule, never the url.

    **THE TOKEN PRINTED IS THIS PACKAGE'S OWN CONSTANT**, not a string read off
    a page, so naming it discloses nothing. The landed url is NEVER printed:
    one carrying his vanity slug is exactly what the identity apparatus exists
    to keep out of files and transcripts, and a probe that printed it to
    explain a refusal would reproduce the defect it documents.

    The two refusals are different rulings wearing one word:

    * a FORBIDDEN SUBSTRING is a deliberate class ban, checked before the
      allowlist is consulted at all;
    * NO PATTERN MATCHING is the absence of a permission rather than the
      presence of a prohibition -- nobody ruled on it.
    """
    if readonly.is_read_url(url):
        return "admitted"
    exemptions = getattr(readonly, "_FORBIDDEN_SUBSTRING_EXEMPTIONS", {}) or {}
    if url in exemptions:
        return "exempted from a substring, then refused by NO PATTERN"
    for token in getattr(readonly, "_FORBIDDEN_URL_SUBSTRINGS", ()) or ():
        if token in url:
            return "FORBIDDEN SUBSTRING %r (a deliberate class ban)" % token
    return "NO PATTERN MATCHES (absence of a permission, not a prohibition)"


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
        print("    refused ON: %s" % _why_refused(str(landed)))
    return landed_admitted


async def main() -> int:
    print("=== DO ADMITTED ADDRESSES STAY ADMITTED AFTER THE REDIRECT?")
    print("    Only addresses shipped tools already load. No write is fired.")
    print()
    print("    NOT SWEPT, and the exclusions are part of the answer:")
    for address, why in NOT_SWEPT:
        print("      %-18s %s" % (address, why))
    print()
    print("    SCOPE, because it bounds the result: this gates on is_read_url")
    print("    BEFORE navigating, so it can only measure landings for addresses")
    print("    ALREADY ADMITTED. It answers 'do admitted addresses stay")
    print("    admitted', never 'should a refused address be admitted'.")

    _own_page = None
    refused_after_landing = 0
    measured = 0
    try:
        async with BROWSER.session() as page:
            _own_page = page
            order = list(SWEEP)
            if "--reverse" in sys.argv:
                # SAME ROWS, DIFFERENT PREDECESSOR FOR EVERY ONE. A second pass
                # in the same order would repeat each row's neighbour too, so a
                # row that agrees with itself would only have shown that the
                # sequence is reproducible.
                control, rest = order[0], order[1:]
                order = [control] + list(reversed(rest))
                print("    ORDER REVERSED: every row has a different predecessor")
                print("    than pass one. The control stays first.")
            for index, (label, url) in enumerate(order):
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
