"""Which job holds the IN-PROGRESS application?

WHY THIS EXISTS. ``linkedin_my_applications`` reports the tracker's tab
counts, and on this account they read ``applied: 0`` and ``in_progress: 1``.
That single number is the most useful fact available about the apply feature:
**an Easy Apply DRAFT is a distinct, counted state that an application never
has to reach.**

It also names the safest possible subject for an apply-flow capture. Opening
the flow for a posting that ALREADY has a draft resumes existing state rather
than creating new state -- so the capture cannot be the thing that made the
draft. Every other posting on LinkedIn would leave that ambiguous.

IT NO LONGER PROBES A SURFACE THE SERVER CANNOT REACH, and this paragraph used
to say it did. **Until 2026-09-19 it read:** *"DELIBERATELY PROBES A SURFACE THE
SERVER CANNOT REACH ... nothing in linkedin_server/ can reach this url and
nothing here changes that."* That was true when written and is false now, in
two separate ways, which is why it is corrected here rather than quietly
dropped.

**The boundary moved under it.** Measured 2026-09-19, the allowlist admits
``?stage=saved``, ``?stage=applied`` AND ``?stage=draft`` -- three, not the two
the old text named -- and still refuses ``?stage=in_progress``.

**And this probe was constrained rather than left outside**, on the ruling in
``_audit/2026-09-19-two-census-conventions-ruled.md`` section 4: a discovery
probe may not navigate to a refused address, even to find out whether it should
be admitted. It now tries only admitted values and goes through
``BROWSER.goto`` like everything else, so the allowlist is a check it PASSES
rather than one it was written to sidestep. The three refused tokens are named
in ``UNMEASURED_STAGES`` below with the reason they were not tried.

It reads. It clicks nothing. It prints ids and counts, never a person.

Run:  python scripts/_probe_in_progress.py
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"
# The tab is LABELLED "In Progress" but the url token is something else:
# ``?stage=in_progress`` returns a page whose <main> never renders at all
# (139 chars of nav shell, measured 2026-08-24). The tracked fixture
# ``jobs_tracker_row.html`` carries a real captured link reading
# ``/jobs-tracker/?stage=draft`` -- so ``draft`` is the leading candidate.
# Every value here is tried in order and the first that RENDERS ROWS wins.
#
# CONSTRAINED TO THE ADMITTED VALUES 2026-09-19, on the ruling in
# ``_audit/2026-09-19-two-census-conventions-ruled.md`` section 4:
# **A DISCOVERY PROBE MAY NOT NAVIGATE TO A REFUSED ADDRESS, EVEN TO FIND OUT
# WHETHER IT SHOULD BE ADMITTED.**
#
# This list was five. Measured against ``readonly.is_read_url`` on 2026-09-19,
# the read boundary admits two of them and refuses three:
#
#     ?stage=draft        ADMITTED
#     ?stage=applied      ADMITTED
#     ?stage=in-progress  REFUSED      <- never tried, and that is the point
#     ?stage=inprogress   REFUSED
#     ?stage=in_review    REFUSED
#     /jobs-tracker/      REFUSED      (the bare form, no query)
#
# **SO THREE CANDIDATE TOKENS ARE UNMEASURED BY THIS PROBE AND WILL STAY THAT
# WAY UNTIL SOMEBODY ADMITS THEM.** Naming them here is the deliverable: a
# probe that reports which values were never tried, and why, is worth more
# than one that tried them without permission.
#
# THE TENSION IS REAL AND WAS RULED AGAINST, WHICH IS WORTH RECORDING BECAUSE
# THE ARGUMENT IS GOOD. A probe that can only try values already known to be
# admitted cannot discover which value is real -- that is true, and it is the
# argument for ADMITTING the three addresses, not for navigating without the
# check. Every bypass in this repository's history was taken for a reason that
# sounded like that one.
#
# The discovery question stays open and is answerable by an admit-and-measure
# wave with its own blast radius and a revert path. What is NOT available is
# answering it from here, quietly, by going anyway.
STAGES = ("draft", "applied")

#: Tried by an earlier form of this probe and NOT tried now, with the reason.
#: Kept as data rather than prose so the next reader sees the shape of what is
#: missing rather than having to infer it from an absence.
UNMEASURED_STAGES = ("in-progress", "inprogress", "in_review")


async def _load(page, url: str, label: str) -> str:
    # ROUTED THROUGH THE GUARDED DOOR 2026-09-19, now that ``STAGES`` holds
    # only admitted values. This hand-rolled the door's body -- rate slot,
    # goto at 45_000, the navigation stamp, networkidle with a flat-wait
    # fallback -- and omitted the one line that is a boundary.
    #
    # ``BROWSER.goto`` is an exact superset: NAV_TIMEOUT_MS IS 45_000 and its
    # settle is the same networkidle-then-flat-wait against the same
    # SETTLE_MS, so nothing here waits differently. What it adds is the
    # allowlist check -- which is now a check this probe PASSES rather than
    # one it needed to avoid.
    await BROWSER.goto(page, url)
    html = await page.content()
    (OUT / f"_probe-tracker-{label}.html").write_text(html, encoding="utf-8")
    print(f"\n=== {label}: {url}")
    print(f"    landed {page.url}")
    return html


async def main() -> None:
    async with BROWSER.session() as page:
        for stage in STAGES:
            html = await _load(page, f"{BASE_URL}/jobs-tracker/?stage={stage}", stage)
            text = await dom.read_main_text(page)
            counts = shape.parse_tracker_tabs(text)
            ids = sorted(set(re.findall(r"/jobs/view/(\d{6,})", html)))
            print(f"    tab counts : {counts}")
            print(f"    job ids on this stage: {len(ids)} -> {ids}")
            if ids:
                print()
                print("    ^ THIS is the safest subject for an apply-flow capture:")
                print("      a draft already exists, so opening the flow resumes")
                print("      state rather than creating it.")
        # WHAT WAS NOT TRIED, REPORTED RATHER THAN OMITTED. An absence a reader
        # has to notice is an absence a reader will not notice, and a probe
        # that silently narrowed its own question looks exactly like one whose
        # question was always narrow.
        print()
        print("=== NOT TRIED, and this is a boundary fact rather than a result")
        for stage in UNMEASURED_STAGES:
            print(f"    ?stage={stage:<12} REFUSED by the read boundary")
        print("    A discovery probe may not navigate to a refused address,")
        print("    even to find out whether it should be admitted --")
        print("    _audit/2026-09-19-two-census-conventions-ruled.md s4.")
        print("    Whether any of these renders rows is UNMEASURED and stays")
        print("    so until an admit-and-measure wave takes it with a revert")
        print("    path. It is not evidence that they do not.")
    await BROWSER.stop()


if __name__ == "__main__":
    asyncio.run(main())
