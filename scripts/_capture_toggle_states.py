"""Capture the ON state of every toggle this server might one day move.

WHY THIS EXISTS. The frozen job fixtures show ``aria-label="Save the job"``
and ``aria-label="Follow"`` and nothing else, because every posting that was
ever captured happened to be one he had not saved, at a company he did not
follow. So the package knows what OFF looks like and has never seen ON -- and
a gate that cannot tell the two apart cannot say which way it is about to move
the toggle. That is not a write problem. It is a READ that nobody performed.

This script performs it. Every navigation goes through
``readonly.assert_read_url`` and the rate limiter, exactly as a tool does;
nothing here clicks anything. It is the same instrument as
``_build_job_fixtures.py`` pointed at a different question.

WHAT IT LOADS, and why each one is the cheapest way to see its state:

  1. ``/jobs-tracker/?stage=saved``   -- which postings are SAVED right now.
  2. ``/jobs/view/<a saved id>/``     -- the Save toggle in its ON state.
  3. ``/jobs-tracker/?stage=applied`` -- which postings he APPLIED to. Applying
     through LinkedIn commonly follows the employer as a side effect, so an
     applied posting is the likeliest place a FOLLOWING state is already
     sitting, with no new surface and no new allowlist entry.
  4. ``/jobs/view/<an applied id>/``  -- the Follow toggle, hopefully ON.
  5. ``/in/me/``                      -- Open To Work: whether it is on, and
     WHO it is shared with.

Raw output lands in ``_audit/_probe-*.html`` and is NEVER committed: it carries
real employers, real job ids and tracking tokens. Sanitising is a separate
step, as it is for the job fixtures.
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, SETTLE_MS  # noqa: E402
from linkedin_server.readonly import assert_read_url  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"

#: Every accessible name worth reporting on sight. The point of the run is to
#: find which of these LinkedIn actually renders, so the list is deliberately
#: wider than what the fixtures already contain.
WATCH = re.compile(
    r'aria-label="([^"]*(?:[Ss]ave|[Ff]ollow|[Aa]pplied|[Oo]pen to|[Rr]emove'
    r'|[Dd]elete|[Uu]nsave|[Uu]nfollow)[^"]*)"'
)


async def capture(page, url: str, name: str) -> tuple[str, str]:
    """Load ``url`` once and freeze it before and after it settles."""
    assert_read_url(url)
    waited = await BROWSER.wait_for_rate_slot()
    print(f"\n=== {name}  (waited {waited}s for the rate slot)\n    {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    BROWSER._last_navigation_at = time.monotonic()
    pre = await page.content()
    try:
        await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
    except Exception:
        await page.wait_for_timeout(SETTLE_MS)
    hyd = await page.content()
    (OUT / f"_probe-{name}-pre.html").write_text(pre, encoding="utf-8")
    (OUT / f"_probe-{name}-hyd.html").write_text(hyd, encoding="utf-8")
    print(f"    final url : {page.url}")
    print(f"    pre {len(pre):>7} chars   hyd {len(hyd):>7} chars")
    for state, html in (("pre", pre), ("hyd", hyd)):
        labels = sorted(set(WATCH.findall(html)))
        print(f"    {state} aria-labels of interest: {labels}")
    return pre, hyd


def job_ids(html: str) -> list[str]:
    seen: list[str] = []
    for jid in re.findall(dom.JOB_HREF, html):
        if jid not in seen:
            seen.append(jid)
    return seen


async def main() -> None:
    async with BROWSER.session() as page:
        _, saved_hyd = await capture(
            page, f"{BASE_URL}/jobs-tracker/?stage=saved", "tracker-saved"
        )
        saved = job_ids(saved_hyd)
        print(f"\n    SAVED job ids ({len(saved)}): {saved[:12]}")

        if saved:
            await capture(
                page, f"{BASE_URL}/jobs/view/{saved[0]}/", "job-saved-on"
            )

        _, applied_hyd = await capture(
            page, f"{BASE_URL}/jobs-tracker/?stage=applied", "tracker-applied"
        )
        applied = job_ids(applied_hyd)
        print(f"\n    APPLIED job ids ({len(applied)}): {applied[:12]}")

        if applied:
            await capture(
                page, f"{BASE_URL}/jobs/view/{applied[0]}/", "job-applied"
            )

        await capture(page, f"{BASE_URL}/in/me/", "profile-me")

    await BROWSER.stop()


asyncio.run(main())
