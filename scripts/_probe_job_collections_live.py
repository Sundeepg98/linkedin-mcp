"""Does the recommended-jobs collection render anything, and what SHAPE is a row?

``JOB-COLLECTIONS-SURFACE`` (census `J 42`) is one row and its address --
``/jobs/collections/recommended/`` -- has been on the read allowlist since
``tests/test_school_and_collections_boundary.py`` admitted it. **The boundary is
open and there is no reader behind it**, which is Amendment A10's shape: a
pattern admitted with nothing built on it.

Nobody in this repository has opened the page. So the row cannot be costed: a
reader written against an imagined DOM fails CLOSED as *"he has no
collections"* -- the exact answer the surface exists to produce -- which is the
trap the newsletter wave named and correctly refused to walk into.

THIS SCRIPT OPENS IT ONCE AND MEASURES.

**THAT SENTENCE USED TO END "AND BUILDS NOTHING. Its output is the input a
reader needs and does not have."** It was true when written and is not any
more: the reader exists (``linkedin_server.collections_page``, 2026-09-19) and
this script now RUNS it, beside the census, on the same load. Corrected rather
than left, because a module docstring is a STANDING INSTRUCTION -- whoever opens
this file next reads it as current truth -- and this repository has watched a
stale premise propagate through exactly that channel.

## THE POSITIVE CONTROL RUNS FIRST AND THE SCRIPT ABORTS WITHOUT IT

The first live read here matched ZERO of the five groupings, and **a matcher
that returns zero everywhere is indistinguishable from a broken one.** So before
any page is opened, the same in-page matcher is run against a DETACHED
container built from a synthetic fixture -- no navigation, no page load. It must
match 5 and leave the decoy unmatched. If it does not, every zero below would be
meaningless and this script says so and stops, rather than reporting a number
nobody can read.

## WHAT LEAVES THIS PROCESS: INTEGERS, SHAPES AND VERDICTS

Every control goes through ``dom.read_surface_census``, which shapes each name
and href inside itself. Nothing here prints a navigation-derived url: the
landed address becomes a RELATION before any print, via the ``_relation``
helper copied BYTE-IDENTICALLY from ``scripts/_probe_groups_events_live.py``,
where it was admitted to the sanitiser list WITH the test that proves its
contract. Copied rather than imported for the same reason its siblings are:
these probes do not import each other.

## THE BADGE IS READ BEFORE AND AFTER, and that is not ceremony

This repository's own discipline for proving a read did not consume something
it passed. ``/jobs/`` is not believed to touch the invitation counter -- which
is exactly why it is worth reading: a control that must NOT move, and does not,
is the only evidence that the instrument can tell the difference.

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_job_collections_live.py
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from linkedin_server import collections_page, dom, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: The address under test. One row, and the reason this script exists.
COLLECTIONS_URL = "https://www.linkedin.com/jobs/collections/recommended/"

#: A known-served address, read first and last. Without it a zero everywhere is
#: a fact about the session rather than about the surface.
CONTROL_URL = "https://www.linkedin.com/jobs/search/"

#: A job posting's entity segment is PURE DIGITS, the same rule
#: ``linkedin_server/groups.py`` applies to a group id and for the same reason:
#: a non-numeric segment is a slug, and a slug is a name.
JOB_MARKER = "/jobs/view/"


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


def _href_classes(controls: list) -> dict[str, int]:
    """A HISTOGRAM OF ROUTE CLASSES, which is what a reader must key on.

    The first two path segments of a LinkedIn url are a ROUTE
    (/jobs/collections, /jobs/view), not an identity -- the entity id,
    where there is one, lives in the third. So this counts classes and can
    carry no member, company or posting id by construction.

    THIS EXISTS BECAUSE THE FIRST MARKER READ ZERO ON ITS OWN CONTROL. A
    /jobs/view/ tally returned 0 on the jobs-search page, which certainly
    lists jobs -- so the zero measured the marker, not the surface. A guard
    that cannot fire on the one input that matters is the defect this
    repository names most often, and the remedy is to stop guessing the anchor
    and enumerate what is actually drawn.
    """
    out: dict[str, int] = {}
    for control in controls:
        # has_href and href_shape ARE THE FIELDS. There is no href:
        # read_surface_census shapes every address inside itself and never
        # hands a raw one out. Asking it for href returns nothing on every
        # control -- measured, 147 of 147 on a page made entirely of links --
        # which looks exactly like a page with no links and is instead the
        # boundary working as designed.
        if not (control or {}).get("has_href"):
            out["(no href)"] = out.get("(no href)", 0) + 1
            continue
        shape = str((control or {}).get("href_shape") or "(shape absent)")
        out[shape] = out.get(shape, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1])[:14])


def _job_tally(controls: list) -> dict[str, int]:
    """Count posting-shaped hrefs. COUNTS AND CLASSES, never an id.

    The numeric/non-numeric split is the measurement that matters for a future
    reader: if every entity segment is digits, a name-free reader is possible
    on this surface; if any is a slug, it is not, and that is a ruling rather
    than a parsing problem.
    """
    total = numeric = slugged = 0
    for control in controls:
        href = str((control or {}).get("href") or "")
        if JOB_MARKER not in href:
            continue
        total += 1
        tail = href.split(JOB_MARKER, 1)[1].split("/")[0].split("?")[0]
        if tail.isdigit():
            numeric += 1
        elif tail:
            slugged += 1
    return {"posting_hrefs": total, "numeric": numeric, "non_numeric": slugged}


async def _badge(page, label: str) -> None:
    """The counter that must NOT move. Printed as its own integers only."""
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


async def _read(page, label: str, url: str) -> dict:
    print(f"\n--- {label}")

    # THE BOUNDARY IS ASKED FIRST. If the allowlist ever loses this entry, this
    # refuses here rather than from inside a navigation.
    if not readonly.is_read_url(url):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return {"refused": True}

    landed = await BROWSER.goto(page, url)
    relation = _relation(landed, url)
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    print(f"    relation: {relation}")
    if walled:
        print("    AUTH WALL. Nothing else measured.")
        return {"authwall": True}

    # THE READER, beside the census, so both are taken on the SAME load rather
    # than compared across runs -- this surface's counts move between loads.
    grouping_read = await collections_page.read_collections(page)
    grouping_tally = collections_page.tally(
        grouping_read["indices"], grouping_read["cards"])
    print(f"    groupings    : matched={grouping_tally['matched_groupings']}  "
          f"unmatched={grouping_tally['unmatched_headings']}  "
          f"nodes={grouping_read['headings_seen']}")

    census = await dom.read_surface_census(page)
    controls = list(census.get("controls") or [])
    counts = census.get("counts") or {}
    jobs = _job_tally(controls)
    print(f"    controls_read={int(census.get('controls_read') or 0)}  "
          f"truncated={bool(census.get('truncated'))}")
    print("    " + "  ".join(
        f"{key}={int(counts.get(key) or 0)}"
        for key in ("forms", "buttons", "links", "contenteditable", "dialogs")
    ))
    print(f"    posting hrefs: {jobs}")
    print(f"    href classes : {_href_classes(controls)}")
    return {"relation": relation, "jobs": jobs,
            "controls": int(census.get("controls_read") or 0)}


async def main() -> int:
    if os.environ.get("LINKEDIN_CDP_ATTACH") != "1":
        print("REFUSED: run with LINKEDIN_CDP_ATTACH=1. Launch mode would open "
              "a SECOND Chrome on the signed-in profile, which is the "
              "2026-08-25 failure that cost the session.")
        return 2

    print("=== JOB COLLECTIONS, LIVE. One row, an open boundary, no reader.")
    print("    Integers, shapes and verdicts only.")

    page_ref = None
    try:
        async with BROWSER.session() as page:
            page_ref = page
            print("\n### POSITIVE CONTROL FIRST, and it needs no page load.")
            print("    The same in-page matcher over a DETACHED container.")
            print("    A matcher that returns zero everywhere is")
            print("    indistinguishable from a broken one, so this must")
            print("    fire before any zero below means anything.")
            fixture = await collections_page.read_collections(
                page, collections_page.control_fixture())
            fixture_tally = collections_page.tally(
                fixture["indices"], fixture["cards"])
            matched = int(fixture_tally["matched_groupings"])
            decoys = int(fixture_tally["unmatched_headings"])
            print(f"    matched_groupings : {matched}  (MUST be "
                  f"{len(collections_page.GROUPINGS)})")
            print(f"    unmatched decoy   : {decoys}  (MUST be 1)")
            if matched != len(collections_page.GROUPINGS) or decoys != 1:
                print("    THE MATCHER CANNOT MATCH, or cannot discriminate.")
                print("    EVERY ZERO BELOW WOULD BE MEANINGLESS. Aborting")
                print("    rather than reporting a zero nobody can read.")
                return 1

            print("\n### CONTROL PAGE. If this is wrong, nothing else is a reading.")
            control_first = await _read(page, "CONTROL  jobs search", CONTROL_URL)
            await _badge(page, "before")

            first = await _read(page, "COLLECTIONS 1", COLLECTIONS_URL)
            second = await _read(page, "COLLECTIONS 2", COLLECTIONS_URL)

            await _badge(page, "after")
            print("\n### CONTROL AGAIN, at the end of the session.")
            control_second = await _read(page, "CONTROL  jobs search", CONTROL_URL)
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
        # CLOSE THE TAB THIS RUN OPENED. In ATTACH mode ``BROWSER._page()``
        # caches the page and ``session()``'s finally only touches an idle
        # timer, so the tab OUTLIVES THE PROCESS -- one leaked tab per probe
        # run in the operator's own Chrome. THE PAGE, NEVER THE CONTEXT: the
        # context is his signed-in browser session.
        if page_ref is not None:
            try:
                await page_ref.close()
                print("\n    tab closed")
            except Exception as error:  # noqa: BLE001
                print(f"\n    tab NOT closed: {type(error).__name__}")

    print("\n=== VERDICT")
    ok = (control_first.get("controls") or 0) > 0 and (control_second.get("controls") or 0) > 0
    print(f"    controls behaved at both ends : {ok}")
    if not ok:
        print("    THE CONTROL DID NOT FIRE. Every zero below is a fact about "
              "this session, not about the surface. Nothing here is a reading.")
        return 1
    print(f"    collections relation, read 1  : {first.get('relation')}")
    print(f"    collections relation, read 2  : {second.get('relation')}")
    print(f"    posting hrefs, read 1         : {first.get('jobs')}")
    print(f"    posting hrefs, read 2         : {second.get('jobs')}")
    print("    TWO READS: a count that differs across them is a fact about the "
          "surface's stability, not about the reader.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
