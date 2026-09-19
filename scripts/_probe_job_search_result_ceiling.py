"""SEVEN. THIRTEEN TIMES OUT OF THIRTEEN. Why?

``scripts/_probe_job_search_result_sets.py`` measured the five shipped job
filters on the result-set channel and they all move the set. It measured
something else on the way, on every one of its thirteen loads, across two
professions and two cities:

    cards 7   ids 7   rows 7   /jobs/view/ anchors 9   anchors of any kind 24-34

**A NUMBER THAT DOES NOT MOVE UNDER A CHANGE THAT SHOULD MOVE IT IS A NUMBER
ABOUT THE INSTRUMENT.** Nursing in city A and Node in city B share no
postings and both returned exactly seven. A jobs search page holds about
twenty-five. So seven is a CEILING and this file is about where it is.

It is not a timing ceiling. That probe read every page twice -- once where
``server._read_cards`` reads and once six seconds later with nothing pressed --
and the id set grew on 0 of 13 loads. Waiting is not the repair.

THE THREE CANDIDATES, and one load separates them:

1. **THE WALK IS DROPPING ANCHORS.** ``dom.harvest_census`` runs the identical
   script as ``harvest_linked_cards`` under a flag and reports
   ``anchors_keyed`` and ``dropped_empty_text``. If it keyed 9 and dropped 2,
   the walk is the ceiling and the repair is in ``dom.py``.
2. **THE PAGE HOLDS ONLY NINE.** Then the results list is virtualised and the
   DOM never had the other sixteen, so no harvest could have found them. The
   repair is not in the harvest at all.
3. **THE PAGE HOLDS TWENTY-FIVE AND THE PATTERN MATCHES NINE.** Then
   ``dom.JOB_HREF`` is the ceiling.

The page's OWN result count is read as well, because "the tool returns 7" and
"the tool returns 7 of 700" are the same sentence with very different stakes,
and only one of them is worth his morning.

**THE VIEWPORT IS READ TOO, AND IT IS NOT A CURIOSITY.** If the list is
virtualised, how many cards exist depends on how large the operator's window
happens to be -- which would make the tool's output a function of a window
nobody thinks of as a parameter. That is worth knowing before anybody argues
about a scroll.

ONE LOAD. Nothing pressed, nothing scrolled, nothing written.

WHAT IS PRINTED: integers, and text this file matched with its own literal
regular expression. No id, no title, no employer, no url.

Run::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_job_search_result_ceiling.py

Writes ``_audit/_scratch/_probe-jobsearch-ceiling.txt``.
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

#: **THE CITY IS NOT WRITTEN INTO THIS FILE, AND THAT IS A GUARD FINDING
#: RATHER THAN A PREFERENCE.** ``scripts/sweep_tracked_for_identity.py``
#: refused an earlier draft of these probes on three lines across three files:
#: the operator's own city is on its denied list, and a city he lives in is an
#: identifying string whether or not it looks like one. The remedy is not a
#: declaration -- it is to stop putting it in a tracked file. The query is
#: supplied by the environment, the DEFAULT is a whole country and identifies
#: nobody, and the reading is unaffected because none of the questions this
#: file asks are about which city it is::
#:
#:     LINKEDIN_PROBE_CITY_A=<city> ./venv/Scripts/python.exe scripts/<probe>.py
CITY_A = os.environ.get("LINKEDIN_PROBE_CITY_A", "India")
KEYWORD_TEXT = "node.js developer"

#: Built from those two, never from anything a page returned.
#: ``tests/test_navigation_is_never_derived.py`` forbids assembling an address
#: out of a LANDED url; an environment variable and a constant in this file
#: are neither, so this stays inside that rule while keeping the city out.
URL = "https://www.linkedin.com/jobs/search/?" + urlencode(
    {"keywords": KEYWORD_TEXT, "location": CITY_A}
)

#: **LINKEDIN'S OWN COUNT, MATCHED WITH OUR OWN PATTERN.** Two spellings
#: because LinkedIn writes "About 1,234 results" on some renders and
#: "1,234 results" on others, and a search that knew only one would report a
#: confident zero. Only the DIGITS are lifted out, and only after the comma
#: separators are removed, so nothing but an integer leaves this function.
RESULT_COUNT_PATTERNS: tuple[str, ...] = (
    r"About\s+([\d,]+)\s+results?",
    r"([\d,]+)\s+results?",
)

JOB_VIEW_ANCHOR = 'a[href*="/jobs/view/"]'

#: Deliberately far above a page's worth, so a ceiling can never be a limit.
HARVEST_MAX = 200

OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-jobsearch-ceiling.txt"
)


def _count_from_text(text: str) -> int:
    """LinkedIn's own result count, or -1. AN INTEGER OR NOTHING.

    The page text is matched against this file's own literal patterns and only
    a digit run is taken. No matched text is returned and none is printed --
    the caller gets an integer, which is the only thing the question needs.
    """
    for pattern in RESULT_COUNT_PATTERNS:
        match = re.search(pattern, str(text or ""))
        if match:
            try:
                return int(match.group(1).replace(",", ""))
            except ValueError:
                continue
    return -1


async def _count(page, selector: str) -> int:
    try:
        return int(await page.locator(selector).count())
    except Exception:
        return -1


async def main() -> None:
    lines: list = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("=== WHERE IS THE SEVEN-RESULT CEILING?")
    emit("    one load, nothing pressed, nothing scrolled")
    emit("    integers and this file's own literals only")
    emit()

    try:
        await BROWSER.start()
    except Exception as exc:
        emit("    COULD NOT START THE BROWSER: %s: %s"
             % (type(exc).__name__, str(exc)[:300]))
        _write(lines)
        return

    keyed = -1
    dropped = -1
    harvested = -1
    parsed = -1
    refused = -1
    anchors = -1
    all_anchors = -1
    list_items = -1
    linkedin_count = -1
    viewport_w = -1
    viewport_h = -1

    try:
        async with BROWSER.session() as page:
            landed_url = await BROWSER.goto(page, URL)
            # A COMPARISON AGAINST A LITERAL. The boolean is all this file
            # takes off the landed address.
            walled = "/authwall" in landed_url or "/login" in landed_url
            if walled:
                emit("    AUTH WALL. Nothing measured.")
            else:
                try:
                    size = await page.evaluate(
                        "() => [window.innerWidth, window.innerHeight]"
                    )
                    viewport_w, viewport_h = int(size[0]), int(size[1])
                except Exception:
                    pass

                anchors = await _count(page, JOB_VIEW_ANCHOR)
                all_anchors = await _count(page, "a[href]")
                list_items = await _count(page, "li")

                try:
                    census = await dom.harvest_census(
                        page, href_pattern=dom.JOB_HREF, max_items=HARVEST_MAX
                    )
                    # A CENSUS THAT COULD NOT RUN RETURNS None, NOT ZERO --
                    # that is its own documented refusal, and int(None) would
                    # turn it into a crash where -1 is the honest reading.
                    if census.get("anchors_keyed") is not None:
                        keyed = int(census["anchors_keyed"])
                    if census.get("dropped_empty_text") is not None:
                        dropped = int(census["dropped_empty_text"])
                    harvested = len(census.get("rows") or [])
                except Exception as exc:
                    emit("    harvest_census FAILED: %s" % type(exc).__name__)

                try:
                    records = await dom.harvest_linked_cards(
                        page, href_pattern=dom.JOB_HREF, max_items=HARVEST_MAX
                    )
                    rows, refused_count = dom.parse_all(
                        records, shape.parse_job_card
                    )
                    parsed = len(rows)
                    refused = int(refused_count or 0)
                    if harvested < 0:
                        harvested = len(records)
                except Exception as exc:
                    emit("    harvest FAILED: %s" % type(exc).__name__)

                try:
                    linkedin_count = _count_from_text(await dom.read_main_text(page))
                except Exception as exc:
                    emit("    main text read FAILED: %s" % type(exc).__name__)
    except Exception as exc:
        emit("    THE RUN RAISED: %s (message withheld)" % type(exc).__name__)
    finally:
        await BROWSER.stop()

    emit("=== THE READINGS")
    emit("    LinkedIn's own result count for this query : %s"
         % ("not found" if linkedin_count < 0 else linkedin_count))
    emit("    anchors matching %s on the page : %s"
         % (JOB_VIEW_ANCHOR, anchors))
    emit("    anchors with any href at all               : %s" % all_anchors)
    emit("    <li> elements on the page                  : %s" % list_items)
    emit("    harvest_census anchors_keyed               : %s" % keyed)
    emit("    harvest_census dropped_empty_text          : %s" % dropped)
    emit("    records harvested                          : %s" % harvested)
    emit("    rows parse_job_card accepted               : %s" % parsed)
    emit("    rows parse_job_card refused                : %s" % refused)
    emit("    viewport                                   : %sx%s"
         % (viewport_w, viewport_h))
    emit()

    emit("=== WHICH OF THE THREE CANDIDATES")
    if anchors < 0 or harvested < 0:
        emit("    a reading failed. No verdict.")
    elif keyed >= 0 and keyed > harvested:
        emit("    (1) THE WALK IS THE CEILING. It keyed %d anchors and returned"
             % keyed)
        emit("        %d records, dropping %d for empty text. The repair is in"
             % (harvested, dropped))
        emit("        dom.py, and harvest_census is what names it.")
    elif anchors > harvested:
        emit("    (3) THE PATTERN IS THE CEILING. %d anchors carry /jobs/view/"
             % anchors)
        emit("        and the harvest keyed %d, so dom.JOB_HREF is refusing"
             % keyed)
        emit("        %d of them -- it requires a six-digit run." % (anchors - keyed))
    else:
        emit("    (2) THE PAGE IS THE CEILING. The harvest found everything")
        emit("        there was. The other results are not in this DOM, so no")
        emit("        change to the harvest or the pattern can reach them.")

    if linkedin_count > 0 and parsed >= 0:
        emit()
        emit("    ***  LinkedIn reports %d postings for this query and the tool"
             % linkedin_count)
        emit("    ***  returns %d of them. Every filter verdict, every ranking"
             % parsed)
        emit("    ***  and every shortlist is taken over that window.")

    if viewport_h > 0:
        emit()
        emit("    THE VIEWPORT IS %dx%d. If the list is virtualised, the number"
             % (viewport_w, viewport_h))
        emit("    of postings this tool returns is a function of the size of a")
        emit("    browser window -- which is not a parameter anybody declared.")

    _write(lines)


def _write(lines: list) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print("written to _audit/_scratch/%s" % OUT_PATH.name)


if __name__ == "__main__":
    asyncio.run(main())
