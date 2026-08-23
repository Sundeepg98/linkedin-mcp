"""Re-capture Manage Pages at BOTH hydration states.

The first probe kept only the settled render. This repo's standing rule is
that a parser is frozen at both, because a fix that passed every test while
returning nothing on the other render has already happened here. The
distinction matters more than usual on this surface: the follow control on a
job posting renders only AFTER hydration, so "no Following label" means
NOT-FOLLOWING on one render and NOTHING-KNOWN-YET on the other, and a parser
that conflates them reports the wrong direction for the toggle.

Still outside the allowlist, deliberately -- see ``_probe_interests.py``.
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
URL = f"{BASE_URL}/mynetwork/network-manager/company/"


async def main() -> None:
    async with BROWSER.session() as page:
        print(f"=== UNLISTED SURFACE PROBE (both states): {URL}")
        await BROWSER.wait_for_rate_slot()
        await page.goto(URL, wait_until="domcontentloaded", timeout=45_000)
        BROWSER._last_navigation_at = time.monotonic()
        pre = await page.content()
        try:
            await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
        except Exception:
            await page.wait_for_timeout(SETTLE_MS)
        hyd = await page.content()
        (OUT / "_probe-manage-pages-pre.html").write_text(pre, encoding="utf-8")
        (OUT / "_probe-manage-pages-hyd.html").write_text(hyd, encoding="utf-8")
        print(f"    final url: {page.url}")
        for state, html in (("pre", pre), ("hyd", hyd)):
            labs = sorted(set(re.findall(
                r'aria-label="([^"]*[Ff]ollow[^"]*)"', html)))
            print(f"    {state}: {len(html)} chars, {len(labs)} follow labels, "
                  f"view-names={len(re.findall('data-view-name', html))}")
            print(f"         first three: {labs[:3]}")
    await BROWSER.stop()


asyncio.run(main())
