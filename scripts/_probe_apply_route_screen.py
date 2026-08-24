"""Which of these postings is LinkedIn-hosted? A read-only screen.

WHY IT IS SEPARATE FROM ``_probe_apply_flow.py``. That probe navigates into
the apply surface, which is the step with a side effect worth being careful
about, and it loads the tracker first. Screening candidates through it would
pay that cost once per candidate just to answer "is this one even the right
kind of posting". This script answers ONLY that, by loading the posting page
and reading the apply anchor's aria-label -- the field the apply census
measured as the single reliable discriminator.

IT NEVER TOUCHES AN APPLY URL. It loads ``/jobs/view/<id>/`` and nothing else.
No click, no fill, no press, and no navigation to ``/apply/``.

Run:  python scripts/_probe_apply_route_screen.py <id> [<id> ...]
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, SETTLE_MS  # noqa: E402

#: The two measured labels, from the apply census. Anything else is unknown --
#: never guessed, because the census showed several fields that LOOK like
#: discriminators and are not.
LINKEDIN_HOSTED = "LinkedIn Apply to this job"
OFFSITE = "Apply on company website"


async def screen(page, job_id: str) -> str:
    url = f"{BASE_URL}/jobs/view/{job_id}/"
    await BROWSER.wait_for_rate_slot()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    except Exception as exc:
        print(f"  {job_id}  LOAD FAILED ({type(exc).__name__})")
        return "load_failed"
    BROWSER._last_navigation_at = time.monotonic()

    # WAIT FOR THE CONTROL, NOT FOR A CLOCK. The first version of this screen
    # settled for SETTLE_MS and then read the labels, and reported UNKNOWN with
    # ZERO apply-ish labels for four postings in a row -- which is exactly the
    # false negative the apply census warned about: an unhydrated posting has
    # no apply control because nothing rendered, not because none exists.
    # browser.py already records that networkidle rarely settles on LinkedIn
    # because of its long-poll connections, so a short settle plus a read is a
    # coin toss. Poll for the anchor instead, and say so when it never comes.
    hydrated = False
    for _ in range(12):
        try:
            if int(await page.locator('a[aria-label*="Apply"]').count()) > 0:
                hydrated = True
                break
        except Exception:
            pass
        await page.wait_for_timeout(2_000)

    landed = page.url
    if "expired_jd_redirect" in landed or "/jobs/view/" not in landed:
        print(f"  {job_id}  EXPIRED (redirected to {landed[:70]})")
        return "expired"

    html = await page.content()
    labels = sorted(set(re.findall(r'aria-label="([^"]*[Aa]pply[^"]*)"', html)))
    if LINKEDIN_HOSTED in labels:
        print(f"  {job_id}  LINKEDIN-HOSTED  <-- usable subject")
        return "linkedin_apply"
    if OFFSITE in labels:
        print(f"  {job_id}  offsite")
        return "offsite"
    if not hydrated:
        print(f"  {job_id}  NEVER HYDRATED after 24s -- says nothing about the")
        print(f"           posting's route, only that the page did not render.")
        return "not_hydrated"
    print(f"  {job_id}  UNKNOWN (apply-ish labels: {labels[:3]})")
    return "unknown"


async def main(ids: list) -> None:
    found = []
    async with BROWSER.session() as page:
        for job_id in ids:
            verdict = await screen(page, job_id)
            if verdict == "linkedin_apply":
                found.append(job_id)
    await BROWSER.stop()
    print()
    if found:
        print(f"=== LinkedIn-hosted postings: {found}")
    else:
        print("=== NONE of these is LinkedIn-hosted.")


if __name__ == "__main__":
    args = [a.strip() for a in sys.argv[1:] if a.strip().isdigit()]
    if not args:
        raise SystemExit("usage: python scripts/_probe_apply_route_screen.py <id> [<id> ...]")
    asyncio.run(main(args))
