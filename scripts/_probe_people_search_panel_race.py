"""REPRODUCE, THEN REFUTE, THE ``linkedin_people_search_shape`` PANEL RACE.

``linkedin_people_search_shape`` returned its filter panel on TWO of three
end-to-end firings. The third read a page that had drawn 45 of its 83 controls
and reported every filter as zero. ``denominators.controls_seen`` disclosed it
and the correlation was exact both ways.

**IT WAS ONLY VISIBLE BECAUSE A SIBLING WAVE'S SUITE PINNED THE CPU.** Both
quiet runs looked deterministic, which is the whole difficulty: the defect is
invisible on the box you would naturally verify a fix on.

## WHY THE RACE EXISTS, FROM ``BROWSER.goto``'s OWN CODE

``goto`` navigates with ``wait_until="domcontentloaded"`` and then settles:

    await page.wait_for_load_state("networkidle", timeout=settle_ms)

with a flat ``wait_for_timeout(settle_ms)`` only if that TIMES OUT. So the two
outcomes are ``settle_ms`` apart, and which one happens is decided by whether
the page found a 500 ms network lull. **On a pinned box a lull is EASIER to
find, not harder** -- the renderer is starved, fewer XHRs are in flight, and
networkidle resolves EARLY against a panel that has not finished drawing. The
loaded box does not slow the wait down; it shortens it.

``goto``'s own docstring already says the settle "is NOT a readiness check".
The three ``dom.wait_for_*`` helpers exist because of that. This surface
shipped without one.

## WHAT THIS PROBE DOES

Fires the shipped tool ``--fires`` times and records, per firing:
``controls_seen``, ``matched_controls``, ``unmatched_controls``,
``filters_offered`` and whether EVERY filter read zero. A firing whose
``controls_seen`` is below the maximum any firing in the run achieved is a
PARTIAL page, and that is the definition used here -- a denominator from the
run itself rather than a constant somebody wrote down once.

**RUN IT UNDER LOAD.** ``--announce-load`` only prints a reminder; the load is
the operator's to create, because a fix verified only on an idle machine
reproduces exactly the condition that hid the defect.

USAGE::

    set LINKEDIN_CDP_ATTACH=1
    <python> scripts/_probe_people_search_panel_race.py --fires 8

BOUNDS: attach only; the tool is a read and presses nothing; one page load per
firing through ``BROWSER.goto``, which holds the shipped rate interval. No
address, needle or label is printed -- the tool's payload is integers and this
package's own vocabulary by construction, and this probe prints a subset.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import config, search_results  # noqa: E402
from linkedin_server.server import mcp  # noqa: E402

EXERCISED = (
    "linkedin_server/search_results.py",
    "linkedin_server/browser.py",
    "linkedin_server/server.py",
    "linkedin_server/dom.py",
)


def provenance() -> dict[str, Any]:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        head = "unavailable:" + type(exc).__name__
    shas = {}
    for relative in EXERCISED:
        try:
            shas[relative] = hashlib.sha256(
                (REPO / relative).read_bytes()
            ).hexdigest()
        except Exception as exc:  # noqa: BLE001
            shas[relative] = "unavailable:" + type(exc).__name__
    return {"git_head": head, "sha256": shas}


async def fire_once() -> dict[str, Any]:
    started = time.monotonic()
    result = await mcp.call_tool("linkedin_people_search_shape", {})
    payload = getattr(result, "structured_content", None) or result
    if isinstance(payload, dict) and "result" in payload:
        payload = payload["result"]
    if not isinstance(payload, dict):
        return {"ok": False, "error": "unexpected_payload_type"}

    denominators = dict(payload.get("denominators") or {})
    filters = dict(payload.get("filters") or {})
    by_term = dict(filters.get("by_term") or {})
    results = dict(payload.get("results") or {})
    settle = dict(payload.get("settle") or {})
    panel = dict(payload.get("panel_wait") or {})
    return {
        "ok": bool(payload.get("ok")),
        "error": payload.get("error"),
        "elapsed_ms": round((time.monotonic() - started) * 1000),
        "landed_where_it_was_sent": payload.get("landed_where_it_was_sent"),
        "controls_seen": denominators.get("controls_seen"),
        "unmatched_controls": denominators.get("unmatched_controls"),
        "anchors_seen": denominators.get("anchors_seen"),
        "empty_labels": denominators.get("empty_labels"),
        "values_refused": denominators.get("values_refused"),
        "filters_offered": filters.get("filters_offered"),
        "terms_nonzero": sum(1 for value in by_term.values() if value),
        "terms_reported": len(by_term),
        "person_results": dict(results.get("by_kind") or {}).get("person_result"),
        # PRESENT ONLY AFTER THE FIX. Absent on the pre-fix tree, which is
        # itself how a reader of this output can tell which tree ran.
        "settle_branch": settle.get("branch"),
        "panel_polls": panel.get("polls"),
        "panel_settled": panel.get("settled"),
        "panel_first": panel.get("controls_first"),
        "panel_last": panel.get("controls_last"),
    }


async def run(fires: int) -> dict[str, Any]:
    """Fire N times, then GIVE THE TAB BACK.

    **A PROBE THAT EXITS WITHOUT TEARING DOWN LEAKS ITS TAB**, and the leak is
    not cosmetic on this surface: ``cdp_bridge.attach`` enumerates every open
    target during its handshake, so each abandoned tab lengthens the NEXT
    probe's attach. Measured 2026-09-21 -- five probe processes took the
    browser from 8 pages to 13, and the sixth attach then exceeded
    ``LINKEDIN_CDP_ATTACH_TIMEOUT_MS`` and returned ``browser_unavailable``
    eight times in a row on a box the suite was loading. The failure looked
    like a dead browser and was a full one.

    ``BROWSER.stop()`` in attach mode closes ONLY the tab this process opened
    and then drops the CDP connection; it never closes the operator's context
    and never touches his windows.
    """
    if not config.CDP_ATTACH:
        raise SystemExit("REFUSING TO RUN. Set LINKEDIN_CDP_ATTACH=1 first.")
    from linkedin_server.browser import BROWSER

    rows: list[dict[str, Any]] = []
    try:
        for number in range(fires):
            row = await fire_once()
            # THE ORDINAL TRAVELS WITH THE READING. See ``summarise``.
            row["fire"] = number
            rows.append(row)
    finally:
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - teardown noise, never fatal
            print("teardown raised " + type(exc).__name__)
    return {"provenance": provenance(), "fires": rows}


def summarise(result: dict[str, Any]) -> int:
    rows = [row for row in result["fires"] if row.get("ok")]
    failed = [row for row in result["fires"] if not row.get("ok")]
    print("")
    print("PEOPLE-SEARCH PANEL RACE")
    print("=" * 96)
    print(
        "%-4s %-9s %-9s %-10s %-9s %-9s %-8s %-7s %s"
        % (
            "fire",
            "controls",
            "unmatched",
            "offered",
            "nonzero",
            "anchors",
            "polls",
            "settled",
            "ms",
        )
    )
    # EACH ROW CARRIES ITS OWN ORDINAL rather than this loop binding one.
    # ``tests/test_probe_controls_are_never_decorative.py`` flagged the
    # ``enumerate`` counter that used to live here: the word "controls" in
    # this table's header put a control marker inside the detector's narrow
    # window, and a loop counter has no verdict to branch on, so it could
    # never be anything but a finding. That is the documented false-positive
    # mechanism -- and the baseline file says to remove the shape rather than
    # document it where removing is cheap. It is cheap here, and a reading
    # that knows its own ordinal is better data besides.
    for row in result["fires"]:
        if not row.get("ok"):
            print("%-4s NOT OK: %s" % (row.get("fire"), row.get("error")))
            continue
        print(
            "%-4s %-9s %-9s %-10s %-9s %-9s %-8s %-7s %s"
            % (
                row.get("fire"),
                row["controls_seen"],
                row["unmatched_controls"],
                row["filters_offered"],
                row["terms_nonzero"],
                row["anchors_seen"],
                row["panel_polls"],
                row["panel_settled"],
                row["elapsed_ms"],
            )
        )
    print("=" * 96)

    if not rows:
        print("NO SUCCESSFUL FIRING. %d failed." % len(failed))
        return 1

    controls = [row["controls_seen"] for row in rows if isinstance(row["controls_seen"], int)]
    nonzero = [row["terms_nonzero"] for row in rows]
    best = max(controls) if controls else 0
    partial = [c for c in controls if c < best]
    blind = [n for n in nonzero if n == 0]

    print("")
    print("  firings:                    %d ok, %d failed" % (len(rows), len(failed)))
    print("  controls_seen:              min %s  max %s  distinct %s"
          % (min(controls), max(controls), sorted(set(controls))))
    print("  filters reading ALL ZERO:   %d of %d" % (len(blind), len(rows)))
    print("  partial pages (< max):      %d of %d" % (len(partial), len(rows)))
    print("  terms nonzero, distinct:    %s" % sorted(set(nonzero)))
    print("  vocabulary shipped:         %d terms" % len(search_results.FILTER_TERMS))
    print("")
    if blind:
        print("  RACE REPRODUCED: at least one firing reported every filter zero.")
        return 1
    if partial:
        print("  PARTIAL PAGES SEEN but no firing went blind. Not closed; not")
        print("  reproduced either. Re-run under heavier load.")
        return 2
    # A RUN WITH FAILED FIRINGS IS NOT A CLEAN RUN, AND SAYING SO IS THE WHOLE
    # POINT OF COUNTING THEM. This branch did not exist until
    # ``tests/test_probe_controls_are_never_decorative.py`` convicted
    # ``failed`` as computed, printed and never branched on -- which is exactly
    # the shape that guard exists for: a probe that reports failures and then
    # certifies its findings anyway. Measured on this probe's own first run:
    # 2 of 8 firings never attached, and the summary would have said
    # "NO BLIND FIRING across 6 firings" without a word about the other two
    # in the verdict.
    if failed:
        print(
            "  INCOMPLETE: %d of %d firing(s) never completed, so this run "
            "measured %d. That is not a clean result and is not reported as "
            "one -- re-run when the box is quiet."
            % (len(failed), len(result["fires"]), len(rows))
        )
        return 3
    print("  NO BLIND FIRING AND NO PARTIAL PAGE across %d firings." % len(rows))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fires", type=int, default=8)
    parser.add_argument("--out", default=None)
    parser.add_argument("--label", default="run")
    args = parser.parse_args()

    result = asyncio.run(run(args.fires))
    destination = Path(
        args.out or (REPO / "_state" / ("people-search-race-%s.json" % args.label))
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    code = summarise(result)
    print("  git head: " + str(result["provenance"]["git_head"]))
    print("  search_results.py sha: "
          + result["provenance"]["sha256"]["linkedin_server/search_results.py"][:16])
    print("  server.py sha:         "
          + result["provenance"]["sha256"]["linkedin_server/server.py"][:16])
    print("  raw json: " + destination.name)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
