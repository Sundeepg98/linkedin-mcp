"""One anchor reader, three surfaces, and the controls that make its numbers mean something.

``linkedin_server.anchors`` classifies a page's anchors by ROUTE SHAPE, shipping
its table INTO the page and getting back integer indices, so no href crosses the
CDP boundary. This runs it against the three read-tail surfaces that needed it.

## THE CONTROL RUNS FIRST AND THIS ABORTS WITHOUT IT

A classifier that returns one class for everything looks exactly like a working
one on a uniform page. So before any navigation, the same in-page classifier is
run against a DETACHED container built from ``anchors.control_fixture()`` -- no
page load -- and its result is compared against ``anchors.CONTROL_EXPECTATION``,
which is written down. **A control whose result nobody predicted cannot fail.**

The fixture carries the two adversarial anchors that convicted a containment
design: a COMPANY slug containing the ``school`` route term, and a MEMBER slug
containing the ``company`` term. Both are synthetic and deliberately not people.

## THE SURFACES ARE INTERLEAVED, AND THAT IS THE SECOND CONTROL

An earlier run read collections and jobs-search back to back and got
near-identical profiles, which has two explanations: LinkedIn serves one
job-list shell for both, or the SPA did not re-render between two adjacent
navigations. Reading a STRUCTURALLY DIFFERENT page between them, and reading
collections twice, separates those.

**AND THE FIRST RUN'S ANSWER DID NOT SURVIVE THE SECOND, which is why this
paragraph reads the way it does.** Run 1: premium repeated exactly, collections
did not -- which looked like *the reader is deterministic and the surface is
not*. Run 2, minutes later, FLIPPED BOTH: premium differed and collections
repeated.

So that discrimination is NOT established, and the honest reading is narrower:
**both of these surfaces move between loads, and which one happens to repeat is
itself unstable across runs.** A single run of a comparison is not a
comparison.

**THE READER'S DETERMINISM IS PROVEN ELSEWHERE AND BETTER** -- by the detached
control fixture, which reproduced ``CONTROL_EXPECTATION`` exactly on every run.
That is the only place the input is held constant, so it is the only place
determinism can be read at all. A live repeat varies the DOM and the reader
together and cannot separate them.

## WHAT LEAVES THIS PROCESS

Counts per class, integers, and relations. The landed address becomes a
RELATION before any print, via the ``_relation`` helper copied BYTE-IDENTICALLY
from ``scripts/_probe_groups_events_live.py``, where it was admitted to the
sanitiser list WITH the test that proves its contract.

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_anchor_surfaces_live.py
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from linkedin_server import anchors, dom, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: Interleaved deliberately -- see the module docstring.
SURFACES: tuple[tuple[str, str], ...] = (
    ("collections A", "https://www.linkedin.com/jobs/collections/recommended/"),
    ("premium (breaker)", "https://www.linkedin.com/premium/my-premium/"),
    ("collections B", "https://www.linkedin.com/jobs/collections/recommended/"),
    ("jobs search", "https://www.linkedin.com/jobs/search/"),
    ("premium again", "https://www.linkedin.com/premium/my-premium/"),
)


def _relation(landed: str, asked: str) -> str:
    """Did the address serve, or did LinkedIn send us somewhere else?

    THE INTERESTS LESSON, applied. ``/in/me/details/interests/`` is on the
    allowlist and REDIRECTS to the profile, so an admitted address is not a
    served one -- and a probe that does not compare the landed url to the
    requested one cannot tell those apart.

    RETURNS A RELATION AND NEVER A URL. Every branch below yields a literal or
    an integer depth; no part of either input survives into the result. The
    depths are taken with ``len`` rather than a helper, because counting a
    thing is the discipline this package uses INSTEAD of printing it, and
    ``tests/test_navigation_is_never_derived.py`` recognises that form.

    ITS LOCALS ARE NAMED FOR THIS FUNCTION, and that is not cosmetic. The
    consent guard tracks tainted names ACROSS A WHOLE MODULE, not per scope,
    so a local called ``before`` here made every ``before`` in this file read
    as navigation-derived -- including three in the cost report, which are
    tallies of shaped control names and touch no url at all. Three of that
    guard's four findings against this file were that collision.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


async def _badge(page, label: str) -> None:
    """The counter that must NOT move. Its own integers only."""
    try:
        read = await dom.read_invitation_badge(page)
    except Exception as error:  # noqa: BLE001
        print(f"    badge {label}: UNREADABLE ({type(error).__name__})")
        return
    # INTEGERS AND A PRESENCE FLAG. The badge's ``label`` is a raw page string
    # -- measured 2026-09-19, it came back as a nav element's accessible name --
    # and printing it is exactly what this wave's reader exists to avoid. It
    # carries no member name today, and that is a fact about what LinkedIn
    # happens to put there rather than a property anything enforces. The
    # navigation taint guard does not cover it, because a badge is not
    # navigation-derived; nothing else did either. So it is counted, not shown.
    shown = {
        key: value for key, value in sorted(read.items())
        if key != "raw" and isinstance(value, (int, bool)) and not isinstance(value, str)
    }
    has_label = bool(read.get("label"))
    print(f"    badge {label}: " + "  ".join(
        f"{key}={value!r}" for key, value in shown.items()
    ) + f"  label_present={has_label}  error={read.get('error') is not None}")


async def _control(page) -> bool:
    print("\n### POSITIVE CONTROL -- detached container, no page load.")
    read = await anchors.read_anchors(page, anchors.control_fixture())
    counted = anchors.tally(read["counts"])
    got = {key: value for key, value in counted["by_class"].items() if value}
    want = dict(anchors.CONTROL_EXPECTATION)
    print(f"    anchors_seen : {read['anchors_seen']}")
    print(f"    matches its written expectation : {got == want}")
    if got != want:
        disagree = {
            key: (want.get(key), got.get(key))
            for key in sorted(set(want) | set(got))
            if want.get(key) != got.get(key)
        }
        print(f"    DISAGREEMENTS (want, got) : {disagree}")
        return False
    return True


async def _read(page, label: str, url: str):
    print(f"\n--- {label}")
    if not readonly.is_read_url(url):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return None
    landed = await BROWSER.goto(page, url)
    relation = _relation(landed, url)
    print(f"    relation : {relation}")
    if "/login" in str(landed) or "/checkpoint" in str(landed):
        print("    AUTH WALL. Nothing else measured.")
        return None
    read = await anchors.read_anchors(page)
    counted = anchors.tally(read["counts"])
    nonzero = {key: value for key, value in counted["by_class"].items() if value}
    print(f"    anchors_seen : {read['anchors_seen']}")
    print(f"    by_class     : {nonzero}")
    print(f"    member anchors (COUNTED, NEVER DESCRIBED) : "
          f"{counted['member_profile_anchors']}")
    print(f"    entity shape : numeric={read['numeric_entity']} "
          f"non_numeric={read['non_numeric_entity']}")
    return nonzero


async def main() -> int:
    if os.environ.get("LINKEDIN_CDP_ATTACH") != "1":
        print("REFUSED: run with LINKEDIN_CDP_ATTACH=1. Launch mode would open "
              "a SECOND Chrome on the signed-in profile, which is the "
              "2026-08-25 failure that cost the session.")
        return 2

    _own_page = None
    seen: dict[str, object] = {}
    try:
        async with BROWSER.session() as page:
            _own_page = page
            if not await _control(page):
                print("\n    THE CLASSIFIER FAILED ITS OWN CONTROL.")
                print("    Every number below would be meaningless. Stopping")
                print("    rather than reporting a count nobody can read.")
                return 1
            await _badge(page, "before")
            for label, url in SURFACES:
                seen[label] = await _read(page, label, url)
            await _badge(page, "after")
    except Exception as error:  # noqa: BLE001
        name = type(error).__name__
        print(f"\nRUN ABORTED: {name}")
        if "ProfileLocked" in name:
            print("    The Chrome profile is held by another process. This is "
                  "the cross-process guard working, not a defect.")
        else:
            print(f"    {error}")
        return 1
    finally:
        # CLOSE THE TAB THIS RUN OPENED. THE PAGE, NEVER THE CONTEXT: the
        # context is his signed-in browser session.
        if _own_page is not None:
            try:
                await _own_page.close()
                print("\n    tab closed")
            except Exception as error:  # noqa: BLE001
                print(f"\n    tab NOT closed: {type(error).__name__}")

    print("\n=== DID THE SURFACES ACTUALLY DIFFER?")
    print(f"    premium == premium again        : "
          f"{seen.get('premium (breaker)') == seen.get('premium again')}"
          "   (TRUE means the READER is deterministic)")
    print(f"    collections A == collections B  : "
          f"{seen.get('collections A') == seen.get('collections B')}"
          "   (FALSE means the SURFACE moves, not the reader)")
    print(f"    collections == jobs search      : "
          f"{seen.get('collections A') == seen.get('jobs search')}"
          "   (TRUE would mean one shell, or a redirect)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
