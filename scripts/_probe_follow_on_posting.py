"""Two loads: the job-page Follow control, on a company he ALREADY follows.

This closes the last link. The Manage-Pages read named twenty companies he
follows; a job posted by one of them is therefore a page where the posting's
own Follow control MUST be in its ON state. Both urls are on the server's
existing allowlist and both go through ``assert_read_url``: nothing here needs
a new surface, and nothing here clicks.

Why it matters that this control specifically is measured, rather than the one
in the Interests list: the sanctioned ``follow_company`` write acts from
``/jobs/view/{id}/``, and the button there is labelled ``Follow`` with NO
company name -- a different convention from the two follow controls already
measured. An ON-state label inferred from a different control is a guess, and
a guess is what this pass exists to remove.
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, SETTLE_MS  # noqa: E402
from linkedin_server.readonly import assert_read_url  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"

#: Vantrex Systems, id 610427 -- read out of the Manage-Pages capture, one of the
#: twenty pages he follows. Chosen for posting volume, nothing else.
FOLLOWED_COMPANY_ID = "610427"
FOLLOWED_COMPANY_NAME = "Vantrex Systems"


async def load(page, url: str, name: str) -> str:
    assert_read_url(url)
    waited = await BROWSER.wait_for_rate_slot()
    print(f"\n=== {name}  (waited {waited}s)\n    {url}")
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
    print(f"    final url: {page.url}   pre {len(pre)}  hyd {len(hyd)}")
    for state, html in (("pre", pre), ("hyd", hyd)):
        labs = sorted(set(re.findall(
            r'aria-label="([^"]*(?:[Ff]ollow|[Ss]ave)[^"]*)"', html)))
        print(f"    {state} follow/save aria-labels: {labs}")
    return hyd


async def main() -> None:
    async with BROWSER.session() as page:
        search = await load(
            page,
            f"{BASE_URL}/jobs/search/?f_C={FOLLOWED_COMPANY_ID}",
            "search-followed-company",
        )
        ids: list[str] = []
        for jid in re.findall(dom.JOB_HREF, search):
            if jid not in ids:
                ids.append(jid)
        print(f"\n    {FOLLOWED_COMPANY_NAME} job ids ({len(ids)}): {ids[:10]}")
        if not ids:
            print("    NO POSTINGS -- cannot measure the ON state this way.")
            await BROWSER.stop()
            return
        await load(page, f"{BASE_URL}/jobs/view/{ids[0]}/", "job-followed-company")
    await BROWSER.stop()


asyncio.run(main())
