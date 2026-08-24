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

DELIBERATELY PROBES A SURFACE THE SERVER CANNOT REACH. The read allowlist
permits ``?stage=saved`` and ``?stage=applied`` and enumerates them precisely
so a third stage needs a deliberate edit. ``?stage=in_progress`` is not on it.
This is a script, driving Playwright directly, exactly as ``_probe_interests``
and ``_probe_messaging`` did -- nothing in ``linkedin_server/`` can reach this
url and nothing here changes that.

It reads. It clicks nothing. It prints ids and counts, never a person.

Run:  python scripts/_probe_in_progress.py
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, SETTLE_MS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"
# The tab is LABELLED "In Progress" but the url token is something else:
# ``?stage=in_progress`` returns a page whose <main> never renders at all
# (139 chars of nav shell, measured 2026-08-24). The tracked fixture
# ``jobs_tracker_row.html`` carries a real captured link reading
# ``/jobs-tracker/?stage=draft`` -- so ``draft`` is the leading candidate.
# Every value here is tried in order and the first that RENDERS ROWS wins.
STAGES = ("draft", "in-progress", "inprogress", "in_review", "applied")


async def _load(page, url: str, label: str) -> str:
    await BROWSER.wait_for_rate_slot()
    await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    BROWSER._last_navigation_at = time.monotonic()
    try:
        await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
    except Exception:
        await page.wait_for_timeout(SETTLE_MS)
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
    await BROWSER.stop()


if __name__ == "__main__":
    asyncio.run(main())
