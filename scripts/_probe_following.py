"""Two loads: is there a READ that lists the companies he follows?

The Interests section's Companies tab is a client-side radio with no url of
its own and no href anywhere in the DOM -- the same shape as the jobs-tracker
tab strip, but WITHOUT the ``?stage=`` escape hatch that made that one
readable. So the question moves to LinkedIn's dedicated following surfaces.

Both candidates are probed OUTSIDE the server's allowlist, deliberately and
loudly, for the same reason as ``_probe_interests.py``: an allowlist entry for
a page nobody has looked at is speculation. Note in advance that
``/feed/following/`` contains ``/follow``, which is on
``readonly._FORBIDDEN_URL_SUBSTRINGS`` -- so even the allowlist would not be
enough for it. That collision is part of what this probe is measuring.
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, SETTLE_MS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"

TARGETS = (
    ("network-manager-company", f"{BASE_URL}/mynetwork/network-manager/company/"),
)


async def main() -> None:
    async with BROWSER.session() as page:
        for name, url in TARGETS:
            print(f"\n=== UNLISTED SURFACE PROBE: {url}")
            await BROWSER.wait_for_rate_slot()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            except Exception as exc:
                print(f"    navigation failed: {type(exc).__name__}: {exc}")
                BROWSER._last_navigation_at = time.monotonic()
                continue
            BROWSER._last_navigation_at = time.monotonic()
            try:
                await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
            except Exception:
                await page.wait_for_timeout(SETTLE_MS)
            html = await page.content()
            (OUT / f"_probe-{name}-hyd.html").write_text(html, encoding="utf-8")
            print(f"    final url: {page.url}")
            print(f"    {len(html)} chars")
            print(
                "    follow aria-labels:",
                sorted(set(re.findall(r'aria-label="([^"]*[Ff]ollow[^"]*)"', html)))[:20],
            )
            print(
                "    company hrefs:",
                sorted(set(re.findall(r"linkedin\.com/company/([A-Za-z0-9\-_%.]+)", html)))[:30],
            )
            txt = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S | re.I)
            txt = re.sub(r"<[^>]+>", " ", txt)
            print("    text:", re.sub(r"\s+", " ", txt).strip()[:500])
    await BROWSER.stop()


asyncio.run(main())
