"""One load: does he follow anything, and does LinkedIn render a FOLLOWING state?

Deliberately probes a surface that is NOT on ``readonly._ALLOWED_URL_PATTERNS``.
That is stated loudly rather than quietly, and it is why this is a script and
not a tool: the SERVER's guard is untouched: nothing in ``linkedin_server/``
can reach this url. The probe exists to decide whether the surface deserves an
allowlist entry at all, because adding a pattern for a page nobody has looked
at is how an allowlist grows on speculation.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402
from linkedin_server.readonly import is_read_url  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"
#: ``/in/me/`` redirects to whoever is signed in, so this surface needs no
#: identity at all. It used to be a literal vanity slug -- his -- in a tracked,
#: pushed file. The slug was not needed to reach the page; it was needed to
#: reach HIS page, which is what /in/me/ already means.
ME = "me"


async def main() -> None:
    async with BROWSER.session() as page:
        for name, url in (
            ("interests", f"{BASE_URL}/in/{ME}/details/interests/"),
        ):
            # THE LABEL IS DERIVED FROM THE BOUNDARY, NEVER TYPED. It read
            # "UNLISTED SURFACE PROBE" unconditionally, which was true when
            # written and is false now -- this address was admitted to the
            # allowlist since. A label somebody must remember to update is a
            # claim that rots; one computed from the thing it describes cannot.
            listed = "LISTED" if is_read_url(url) else "UNLISTED"
            print(f"\n=== {listed} SURFACE PROBE: {url}")
            # ROUTED THROUGH THE GUARDED DOOR 2026-09-19, and it measures the
            # same thing: NAV_TIMEOUT_MS IS 45_000 and the settle is the same
            # networkidle-then-flat-wait against the same SETTLE_MS.
            await BROWSER.goto(page, url)
            html = await page.content()
            (OUT / f"_probe-{name}-hyd.html").write_text(html, encoding="utf-8")
            print(f"    final url: {page.url}")
            print(f"    {len(html)} chars")
            print(
                "    follow aria-labels:",
                sorted(set(re.findall(r'aria-label="([^"]*[Ff]ollow[^"]*)"', html))),
            )
            print(
                "    'Following' text nodes:",
                len(re.findall(r">\s*Following\s*<", html)),
            )
            print(
                "    company hrefs:",
                sorted(set(re.findall(r"linkedin\.com/company/([A-Za-z0-9\-_%.]+)", html)))[:30],
            )
            txt = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S | re.I)
            txt = re.sub(r"<[^>]+>", " ", txt)
            print("    text:", re.sub(r"\s+", " ", txt).strip()[:700])
    await BROWSER.stop()


if __name__ == "__main__":
    asyncio.run(main())
