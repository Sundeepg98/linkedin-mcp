"""The tool's docstring tells him to page with ``start=25``. It returns 7.

MEASURED 2026-09-05, on his own query, over thirteen loads and then one more:

* every load returned exactly **7** postings -- two professions, two cities,
  five filters, and a baseline re-taken last that returned the identical seven;
* the DOM those reads see carries **9** ``/jobs/view/`` anchors, the walk keys
  **7**, ``dropped_empty_text`` is **0**, ``parse_job_card`` refuses **0**;
* LinkedIn's own count for the query is **2915**.

So the window is 7, and ``linkedin_search_jobs``'s docstring says::

    LinkedIn puts roughly 25 results on a page, so ask for the next page
    deliberately with start=25, start=50 and so on.

**IF THE WINDOW IS 7 AND THE STRIDE IS 25, EIGHTEEN POSTINGS PER PAGE ARE
NEVER RETURNED AND NOTHING SAYS SO.** That is the failure this repository
names everywhere else: not a crash, a quiet shortfall that reads like a
complete answer. A shortlist built that way is missing three quarters of
itself.

**BUT A DEFECT REPORT IS NOT A RECIPE, AND HE NEEDS THE RECIPE.** Before the
docstring can prescribe any stride it must be known whether ``start`` offsets
by ones or by pages -- LinkedIn could reasonably do either, and guessing is how
the 25 got there in the first place. One question, four loads:

    start absent   ->  set S0
    start=7        ->  set S7
    start=14       ->  set S14
    start=25       ->  set S25

**THE VERDICT RESTS ON DISJOINTNESS, NOT ON SIZE.** If ``start`` offsets by
ones, S0, S7 and S14 are pairwise disjoint and their union is 21 -- a stride of
7 tiles the list with no gap and no repeat. If ``start`` is ignored, or
rounds to a page, the sets overlap or repeat, and 7 is not a stride.

S25 is the control on the DOCUMENTED advice: whatever it returns, the postings
between the end of S0 and the start of S25 are the ones the current
instruction skips, and their number is what this file is really measuring.

**AND THE INSTRUMENT NEEDS THE SAME CONTROL EVERY OTHER RUN NEEDED.** The
baseline is taken AGAIN at the end. If the unchanged query returns a different
set by then, the ranking drifted mid-run and no disjointness reading is
evidence of anything.

Set sizes and overlaps only -- no id, title, employer or url. One session,
nothing pressed, nothing scrolled.

Run::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_job_search_paging_stride.py

Writes ``_audit/_scratch/_probe-jobsearch-stride.txt``.
"""
from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

SLEEP_BETWEEN_LOADS_S = 3
HARVEST_MAX = 200
WALL_MARKERS: tuple[str, ...] = ("/login", "/checkpoint", "/authwall", "/uas/login")

#: **THE CITY IS NOT WRITTEN INTO THIS FILE.** The identity sweep refused an
#: earlier draft of these probes: the operator's own city is on its denied
#: list, and a city he lives in is an identifying string whether or not it
#: looks like one. The remedy is not a declaration, it is to stop putting it
#: in a tracked file. The default is a whole country and identifies nobody,
#: and no question this file asks is about which city it is.
CITY_A = os.environ.get("LINKEDIN_PROBE_CITY_A", "India")
KEYWORD_TEXT = "node.js developer"


def _search_url(**extra) -> str:
    """One jobs-search address, built from this file and the environment.

    NOT ASSEMBLED FROM A LANDED URL, which is the property
    ``tests/test_navigation_is_never_derived.py`` enforces and the one this
    subject matter makes most tempting to break. An environment variable and
    a constant defined here are neither a page nor a navigation, so building
    from them keeps that property while keeping the city out of the file.
    """
    query = {"keywords": KEYWORD_TEXT, "location": CITY_A}
    query.update(extra)
    return "https://www.linkedin.com/jobs/search/?" + urlencode(query)


LOADS: tuple[tuple[str, str], ...] = (
    ("start absent", _search_url()),
    ("start=7", _search_url(start=7)),
    ("start=14", _search_url(start=14)),
    ("start=25 (the documented stride)", _search_url(start=25)),
    ("start absent, RE-TAKEN", _search_url()),
)

OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-jobsearch-stride.txt"
)


def _ids(records: list) -> set:
    found = set()
    for record in records or []:
        match = re.search(dom.JOB_HREF, str(record.get("href") or ""))
        if match:
            found.add(match.group(1))
    return found


async def main() -> None:
    lines: list = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("=== DOES start OFFSET BY ONES OR BY PAGES?")
    emit("    the tool's docstring prescribes start=25 and the window is 7")
    emit("    set sizes and overlaps only")
    emit()

    sets: dict = {}
    try:
        await BROWSER.start()
    except Exception as exc:
        emit("    COULD NOT START THE BROWSER: %s: %s"
             % (type(exc).__name__, str(exc)[:300]))
        _write(lines)
        return

    try:
        async with BROWSER.session() as page:
            for index, (label, url) in enumerate(LOADS):
                if index:
                    await asyncio.sleep(SLEEP_BETWEEN_LOADS_S)
                emit("--- LOAD %d  %s" % (index + 1, label))
                try:
                    landed_url = await BROWSER.goto(page, url)
                except Exception as exc:
                    emit("    NAVIGATION FAILED: %s" % type(exc).__name__)
                    continue
                # Comparisons against literals. Booleans only leave this scope.
                walled = any(marker in landed_url for marker in WALL_MARKERS)
                if walled:
                    emit("    AUTH WALL. Stopping.")
                    break
                try:
                    records = await dom.harvest_linked_cards(
                        page, href_pattern=dom.JOB_HREF, max_items=HARVEST_MAX
                    )
                    rows, dropped = dom.parse_all(records, shape.parse_job_card)
                except Exception as exc:
                    emit("    HARVEST FAILED: %s" % type(exc).__name__)
                    continue
                sets[label] = _ids(records)
                emit("    cards %d, ids %d, rows %d, refused %d"
                     % (len(records), len(sets[label]), len(rows), int(dropped or 0)))
                emit()
    except Exception as exc:
        emit("    THE RUN RAISED: %s (message withheld)" % type(exc).__name__)
    finally:
        await BROWSER.stop()

    emit("=== THE DRIFT CONTROL FIRST -- it sets the threshold")
    #: **THIS WAS A GATE AND IT WAS THE WRONG SHAPE.** The first version voided
    #: the whole verdict on any drift at all, and the first live run then
    #: refused a reading where the drift was 2 and every start-pair was
    #: disjoint at 14. A control that answers "is this evidence" with a
    #: yes/no cannot say "yes, by a factor of seven", and throwing away a
    #: result seven times its own noise floor is not caution -- it is the same
    #: mistake as believing one one-tenth its size.
    #:
    #: So the floor is a NUMBER the verdict is compared against, and the two
    #: claims are separated: that ``start`` moves the window at all needs the
    #: difference to beat the floor; that it tiles with NO repeat needs a zero
    #: overlap the floor cannot have manufactured, which is a strictly
    #: stronger claim and is reported as unproven when the floor is not zero.
    first = sets.get("start absent")
    again = sets.get("start absent, RE-TAKEN")
    floor = -1
    if first is None or again is None:
        emit("    a baseline load did not complete. NO VERDICT.")
    else:
        floor = len(first ^ again)
        emit("    the unchanged query, re-taken after every other load: "
             "%d id(s) differ" % floor)
        emit("    THE FLOOR IS %d. A difference at or below it is drift; a" % floor)
        emit("    difference above it is the parameter. An OVERLAP of %d or" % floor)
        emit("    fewer could have been erased by that drift, so a zero")
        emit("    overlap proves 'moves' and does not prove 'never repeats'.")
    stable = floor == 0
    emit()

    emit("=== PAIRWISE")
    labels = [label for label, _u in LOADS if label in sets]
    for i, left in enumerate(labels):
        for right in labels[i + 1:]:
            a, b = sets[left], sets[right]
            emit("    %-32s vs %-32s shared %d, only-left %d, only-right %d"
                 % (left, right, len(a & b), len(a - b), len(b - a)))
    emit()

    emit("=== VERDICT")
    s0, s7, s14 = sets.get("start absent"), sets.get("start=7"), sets.get("start=14")
    s25 = sets.get("start=25 (the documented stride)")
    if floor < 0:
        emit("    the drift control did not complete. No verdict.")
    elif not (s0 and s7 and s14):
        emit("    a load did not complete. No verdict.")
    else:
        union = s0 | s7 | s14
        overlap = len(s0 & s7) + len(s7 & s14) + len(s0 & s14)
        moved = min(len(s0 ^ s7), len(s7 ^ s14))
        emit("    S0 %d, S7 %d, S14 %d, union %d, total pairwise overlap %d"
             % (len(s0), len(s7), len(s14), len(union), overlap))
        emit("    smallest difference between two stride-7 neighbours: %d"
             % moved)
        if moved <= floor:
            emit("    ***  start=7 MOVED %d, at or below the %d-id drift floor."
                 % (moved, floor))
            emit("    ***  Indistinguishable from the ranking changing on its")
            emit("    ***  own. NO VERDICT that start does anything.")
        else:
            emit("    ***  start OFFSETS BY ONES, not by pages. A stride of 7")
            emit("    ***  moved %d ids where drift alone moves %d." % (moved, floor))
            if overlap == 0 and floor == 0:
                emit("    ***  and the three windows TILE: zero overlap against a")
                emit("    ***  zero floor, so %d distinct postings, no repeat."
                     % len(union))
            elif overlap == 0:
                emit("    ***  Overlap is 0, but the floor is %d, so up to %d"
                     % (floor, floor))
                emit("    ***  repeats per pair could be hidden by drift. TILING")
                emit("    ***  IS UNPROVEN; that start advances the window is not.")

        if s25 is not None:
            missed = len(s25 - union)
            emit()
            emit("    THE DOCUMENTED STRIDE: start=25 returned %d postings, of"
                 % len(s25))
            emit("    which %d are outside everything the first three loads saw."
                 % missed)
            if missed > floor:
                emit("    ***  start=25 lands somewhere a stride of 7 has not")
                emit("    ***  reached. Between S0 and S25 lie the postings the")
                emit("    ***  docstring's advice skips, and it says nothing.")

    emit()
    emit("=== WHAT THIS CANNOT SAY")
    emit("    Nothing about ORDER: the sets are compared as sets, so 'the first")
    emit("    seven' is not established, only that the three do not overlap.")
    emit("    Nothing about a window on another viewport, or another query.")
    _write(lines)


def _write(lines: list) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print("written to _audit/_scratch/%s" % OUT_PATH.name)


if __name__ == "__main__":
    asyncio.run(main())
