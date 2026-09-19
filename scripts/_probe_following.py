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
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, SETTLE_MS  # noqa: E402
from linkedin_server.readonly import is_read_url  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"

TARGETS = (
    ("network-manager-company", f"{BASE_URL}/mynetwork/network-manager/company/"),
)


async def main() -> None:
    async with BROWSER.session() as page:
        for name, url in TARGETS:
            # THE LABEL IS DERIVED FROM THE BOUNDARY, NEVER TYPED. It read
            # "UNLISTED SURFACE PROBE" unconditionally, which was true when
            # written and is false now -- this address has since been admitted.
            # A label somebody must remember to update is a claim that rots;
            # one computed from the thing it describes cannot.
            listed = "LISTED" if is_read_url(url) else "UNLISTED"
            print(f"\n=== {listed} SURFACE PROBE: {url}")
            # ROUTED THROUGH THE GUARDED DOOR 2026-09-19, and it measures the
            # same thing: NAV_TIMEOUT_MS IS 45_000 and the door's settle is the
            # same networkidle-then-flat-wait against the same SETTLE_MS.
            try:
                await BROWSER.goto(page, url)
            except Exception as exc:
                print(f"    navigation failed: {type(exc).__name__}: {exc}")
                continue
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


if __name__ == "__main__":
    asyncio.run(main())
