"""How many CDP targets are open, WITHOUT printing where any of them points.

WHY THIS EXISTS RATHER THAN A RULE SAYING "BE CAREFUL WITH curl".

`http://127.0.0.1:9224/json/list` is the natural way to check whether the
automation browser is healthy and whether probes are leaking tabs. Its response
contains, for every open tab, the FULL URL -- and when the operator's own
profile editor is open that is

    https://www.linkedin.com/in/<his real vanity slug>/edit

So the ordinary health check publishes his identifier into whatever ran it: a
terminal, a transcript, a log, or an audit document if somebody pastes the
output. This repo already records his slug reaching a transcript three times,
and the whole identity apparatus exists to stop exactly that.

**It is not caught by anything.** The sweep reads TRACKED FILES; this never
reaches a file. The shape guard reads tracked files too. The hazard is in the
COMMAND, and a command is not a file.

So the remedy is not "remember not to paste it". Remembering is what failed the
other three times. **This prints counts and nothing else**, and it is the only
form of that check anybody should need.

    ./venv/Scripts/python.exe scripts/cdp_targets.py
    ./venv/Scripts/python.exe scripts/cdp_targets.py --port 9224

WHAT IT DELIBERATELY WILL NOT DO: print a url, a title, a target id, or any
substring of any of them. If you need to know WHICH tab something is, you need a
different tool and a reason, and you should think about why the count was not
enough.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
import urllib.error
import urllib.request

DEFAULT_PORT = 9224
#: Long enough for a healthy browser, short enough that a dead one does not
#: hold up a wave. A dead port is the common case when this is run.
TIMEOUT_S = 5


def fetch(port: int) -> list[dict]:
    url = f"http://127.0.0.1:{port}/json/list"
    with urllib.request.urlopen(url, timeout=TIMEOUT_S) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    try:
        targets = fetch(args.port)
    except urllib.error.URLError as exc:
        # A dead port is a normal answer here, not an error to hide. Say so
        # plainly -- a wave reading this needs to know the browser is gone, and
        # the reason must never be mistaken for "zero tabs".
        print(f"port {args.port}: NOT ANSWERING ({type(exc).__name__})")
        print("the browser is down. restart with scripts/start_chrome.ps1 --")
        print("never with playwright's chromium, which would downgrade the profile.")
        return 2
    except (TimeoutError, OSError) as exc:  # noqa: PERF203 - distinct message
        print(f"port {args.port}: NOT ANSWERING ({type(exc).__name__})")
        return 2

    kinds = collections.Counter(t.get("type", "?") for t in targets)
    pages = kinds.get("page", 0)

    print(f"port {args.port}: {len(targets)} target(s)")
    for kind, count in sorted(kinds.items()):
        print(f"  {kind:<12} {count}")

    # The number that actually matters for the leak, stated so nobody has to
    # infer it: browser_ui and iframe targets are not tabs anybody opened.
    print()
    print(f"pages (the leak-relevant count): {pages}")
    if pages > 20:
        print("HIGH. Probe tabs accumulate; connect_over_cdp enumerates every")
        print("target on attach, and a large count is what puts the handshake")
        print("over its ceiling. See tests/test_a_probe_closes_its_own_tab.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
