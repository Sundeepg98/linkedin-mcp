"""Close REDUNDANT duplicate tabs in the attached Chrome. Nothing else.

WHY THIS EXISTS, measured 2026-09-05.

``connect_over_cdp`` enumerates and attaches to EVERY target during the
handshake, so the handshake cost scales with how many targets the browser
holds. Twelve concurrent waves each leaked one tab per probe run -- in attach
mode ``BROWSER._page()`` calls ``ctx.new_page()`` and caches it, while
``session()``'s ``finally`` only touches the idle timer, so the tab outlives
the process. 42 scripts call ``session()``; 5 close their page.

The result was a fleet-wide outage with no commit to blame:

    /json/list   128 targets: 27 page, 48 iframe, 51 worker, 2 browser_ui
    attach       13.6s / 16.6s / 17.5s, and STILL failing at a 60_000 ms
                 ceiling, while /json/version answered in 9 ms

**PAGES ARE THE MINORITY OF TARGETS AND THAT IS THE POINT.** 27 of 128. But a
page owns the iframes and workers under it, so retiring a page retires its
subtree -- which is why closing 20 tabs removes far more than 20 targets, and
why "just raise the timeout" does not hold as the growth continues.

WHAT IT WILL NOT TOUCH, and each exclusion is deliberate:

* **A blank or new tab.** It may be the operator's own.
* **A composer or a messaging url.** It may hold an unsent draft this server
  has no surface to detect.
* **The first tab of every distinct url.** Only genuine duplicates go. Any
  wave that loses one can re-navigate; nothing here is unrecoverable.
* **The browser context.** This closes PAGES over the DevTools HTTP endpoint.
  It never calls ``pw.stop()`` and never closes a context -- in attach mode
  the context is the operator's signed-in browser, and closing it closes his
  window.

It also never kills a process. Killing a browser image reaches the operator's
own Chrome, which is a rule this repo earned the hard way.

Run it with the server's venv:

    ./venv/Scripts/python.exe scripts/close_duplicate_tabs.py            # report only
    ./venv/Scripts/python.exe scripts/close_duplicate_tabs.py --close    # act

It reports before acting, and DEFAULTS TO REPORTING. A tool that closes things
should make you ask for it.
"""

from __future__ import annotations

import collections
import json
import sys
import time
import urllib.request

ENDPOINT = "http://127.0.0.1:9224"
SETTLE_SECONDS = 4


def targets() -> list[dict]:
    raw = urllib.request.urlopen(ENDPOINT + "/json/list", timeout=10).read()
    return json.loads(raw)


def _protected(url: str) -> str | None:
    """Why this tab must be left alone, or None if it is an ordinary page."""
    if not url or url.startswith("about:") or url == "chrome://newtab/":
        return "blank/new tab -- may be the operator's"
    if "compose" in url or "/messaging/" in url:
        return "composer -- may hold an unsent draft"
    return None


def plan(pages: list[dict]) -> tuple[list[dict], set[str], int]:
    kept: set[str] = set()
    doomed: list[dict] = []
    protected = 0
    for t in pages:
        url = t.get("url", "")
        if _protected(url) is not None:
            protected += 1
            continue
        if url in kept:
            doomed.append(t)
        else:
            kept.add(url)
    return doomed, kept, protected


def main() -> int:
    act = "--close" in sys.argv
    before = targets()
    pages = [t for t in before if t.get("type") == "page"]
    kinds = collections.Counter(t.get("type") for t in before)

    print("BEFORE: %d targets  %s" % (len(before), dict(kinds)))
    doomed, kept, protected = plan(pages)
    print("  pages                : %d" % len(pages))
    print("  distinct urls kept   : %d" % len(kept))
    print("  protected (untouched): %d" % protected)
    print("  redundant duplicates : %d" % len(doomed))

    if not doomed:
        print("\nnothing to do.")
        return 0
    if not act:
        print("\nreport only. re-run with --close to act.")
        return 0

    closed = 0
    for t in doomed:
        try:
            urllib.request.urlopen(
                "%s/json/close/%s" % (ENDPOINT, t.get("id")), timeout=8
            ).read()
            closed += 1
        except Exception as exc:  # a tab can vanish under us; that is fine
            print("  could not close one: %s" % type(exc).__name__)

    time.sleep(SETTLE_SECONDS)
    after = targets()
    print("\nclosed %d tab(s)" % closed)
    print("AFTER : %d targets  %s"
          % (len(after), dict(collections.Counter(t.get("type") for t in after))))
    if before:
        print("reduction: %d -> %d targets" % (len(before), len(after)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
