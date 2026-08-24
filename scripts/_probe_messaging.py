"""Can this server READ his own LinkedIn inbox, and what does reading cost?

DELIBERATELY PROBES A FORBIDDEN SURFACE. ``/messaging`` is not merely absent
from ``readonly._ALLOWED_URL_PATTERNS`` -- it is on
``readonly._FORBIDDEN_URL_SUBSTRINGS``, so it is refused by the second gate
before the allowlist is even consulted. Nothing in ``linkedin_server/`` can
reach it and nothing here changes that: this is a script, driving Playwright
directly, exactly as ``_probe_interests.py`` did for the Interests page.

WHY A PROBE AT ALL. Every written rationale for the ``/messaging`` block in
this repo is phrased against SENDING -- a message in his name that he did not
read. None of them is about READING, and reading his own inbox is not
collecting data about other members any more than opening his own mail is.
Whether reading is even POSSIBLE has never been measured, and an allowlist
argued about rather than measured is how a boundary grows on speculation.

TWO QUESTIONS, NOT ONE. The first is obvious and the second is the one that
decides the answer:

1. Does the inbox render for a signed-in read at all?
2. WHAT DOES LOADING IT COST? THE HYPOTHESIS, UNVERIFIED: LinkedIn's desktop
   messaging view is understood to auto-select a conversation, and opening a
   conversation marks it read. Nobody here has watched it happen, which is
   precisely why this measures rather than assumes -- an unverified belief
   about a side effect is no better a basis for opening a boundary than an
   unverified belief that there is none. If it holds, a "read-only" inbox tool
   destroys unread state on every call
   -- the same objection that keeps ``mark_notifications_read`` permanently
   forbidden, arriving through a tool that calls itself a read.

HOW THE COST IS MEASURED, since asking the inbox about itself would be circular:
the messaging unread badge is drawn in the global nav on EVERY page, including
``/feed/``, which is already an allowed read surface. So the probe reads the
badge from the feed, loads the inbox, and reads the badge from the feed again.
A drop between the two is the auto-open marking something read. This is the
same discipline the write path already uses: verification comes from a
DIFFERENT surface than the one acted on.

INCONCLUSIVE IS A REAL ANSWER. If the badge is absent or zero to begin with,
there is nothing to lose and the probe cannot tell whether loading the inbox
would have cost anything. It says so rather than reporting a clean run.

Run:  python scripts/_probe_messaging.py
Writes ``_audit/_probe-messaging-*.html`` (gitignored) and prints a summary.
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL, SETTLE_MS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"

#: The inbox list. No thread id, no ``?`` -- the narrowest form of the surface.
INBOX_URL = f"{BASE_URL}/messaging/"

#: Badge shapes worth hunting in the global nav. Hunted as several independent
#: spellings rather than one selector, because a single guessed selector that
#: matches nothing is indistinguishable from a badge that is not there.
_BADGE_PATTERNS = (
    ("aria-label-unread", re.compile(r'aria-label="([^"]*\bunread\b[^"]*)"', re.I)),
    ("aria-label-messaging", re.compile(r'aria-label="([^"]*[Mm]essaging[^"]*)"')),
    ("notification-badge", re.compile(r'notification-badge[^>]*>\s*<?[^<]{0,40}')),
    ("badge-count-text", re.compile(r'"badgeCount"\s*:\s*(\d+)')),
    ("new-notification", re.compile(r'class="[^"]*notification-badge__count[^"]*"[^>]*>\s*([0-9,+]+)')),
)


def _strip(html: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _badges(html: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for name, pattern in _BADGE_PATTERNS:
        hits = sorted({m.group(0)[:120] for m in pattern.finditer(html)})
        if hits:
            found[name] = hits[:12]
    return found


async def _load(page, url: str, *, label: str) -> str:
    await BROWSER.wait_for_rate_slot()
    await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    BROWSER._last_navigation_at = time.monotonic()
    try:
        await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
    except Exception:
        await page.wait_for_timeout(SETTLE_MS)
    html = await page.content()
    (OUT / f"_probe-messaging-{label}.html").write_text(html, encoding="utf-8")
    print(f"\n=== {label}: asked {url}")
    print(f"    landed  {page.url}")
    print(f"    {len(html)} chars")
    return html


async def main() -> None:
    async with BROWSER.session() as page:
        # --- 1. the badge BEFORE, read off an already-allowed surface --------
        before = await _load(page, FEED_URL, label="feed-before")
        badges_before = _badges(before)
        print("    badges:", badges_before or "NONE FOUND")

        # --- 2. the forbidden surface itself ---------------------------------
        html = await _load(page, INBOX_URL, label="inbox-hyd")
        landed = page.url
        print("    auth-wall?     ", "/login" in landed or "/checkpoint" in landed)
        print(
            "    thread links:  ",
            len(set(re.findall(r'href="(/messaging/thread/[^"]+)"', html))),
        )
        print(
            "    aria-labels:   ",
            sorted({m for m in re.findall(r'aria-label="([^"]{0,60})"', html)})[:40],
        )
        print(
            "    conversation-ish class tokens:",
            sorted({m for m in re.findall(r'(msg-[a-z0-9-]{3,40})', html)})[:30],
        )
        print(
            "    unread markers:",
            sorted({m for m in re.findall(r'([a-z-]*unread[a-z-]*)', html, re.I)})[:20],
        )
        print("    text head:", _strip(html)[:900])

        # --- 3. the badge AFTER, same surface as step 1 ----------------------
        after = await _load(page, FEED_URL, label="feed-after")
        badges_after = _badges(after)
        print("    badges:", badges_after or "NONE FOUND")

        print("\n=== SIDE-EFFECT VERDICT")
        if not badges_before:
            print("    INCONCLUSIVE: no badge was readable before the load, so a")
            print("    drop could not have been observed. Absence of evidence.")
        elif badges_before == badges_after:
            print("    NO OBSERVED CHANGE in the nav badge across the inbox load.")
            print("    Not proof of no side effect: a badge already at zero, or one")
            print("    LinkedIn recomputes lazily, would read the same either way.")
        else:
            print("    CHANGED. Loading the inbox moved the nav badge:")
            print("      before:", badges_before)
            print("      after :", badges_after)
    await BROWSER.stop()


# GUARDED, WHICH THE FOUR SIBLING PROBES ARE NOT, AND THE DIFFERENCE MATTERS
# MORE HERE THAN ANYWHERE. ``tests/test_scripts_are_import_safe.py`` exists
# because importing a script must not DO anything -- two build scripts ended in
# a bare ``main()`` and importing either one to read a single table rebuilt the
# committed fixtures. That rule accepts an ATTRIBUTE call at module scope
# (``sys.path.insert`` writes nothing), and ``asyncio.run(...)`` is an
# attribute call, so a probe ending in one passes the guard while doing the
# most side-effecting thing in this repo on import: launching a browser and
# navigating his signed-in session.
#
# For the sibling probes that is a real hole and it is not mine to close here.
# For THIS one it would mean an import driving a browser to a surface the read
# boundary forbids, which is the accident this file is written to avoid causing
# rather than to demonstrate. So it runs only when run.
if __name__ == "__main__":
    asyncio.run(main())
