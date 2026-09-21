"""DRIVE EVERY ``control_fixture()`` IN THIS PACKAGE THROUGH A REAL JS ENGINE.

## WHAT WAS WRONG, STATED AS A MEASUREMENT AND NOT AS A WORRY

Four shipped modules -- ``anchors``, ``search_results``, ``collections_page``
and ``company_root`` -- each declare a ``control_fixture()``. **Three of the
four declared a written-out EXPECTATION beside it; ``collections_page`` did
not, which this probe found on its first run and which is now repaired at the
source** (``collections_page.CONTROL_EXPECTATION``, 2026-09-21). Until then it
was the one control in the package that could not have failed even once
something executed it. ``company_root.read_company_root`` says the rest in its
own docstring:

    **THE SAME IS TRUE OF EVERY SIBLING CONTROL FIXTURE IN THIS PACKAGE** --
    ``anchors``, ``search_results`` and ``collections_page`` all declare one
    and none is driven through a browser by any test. Exercising it needs a
    real engine, which is a browser slot this wave did not have.

That is a sharper defect than a check that cannot fail. **A check that cannot
fail has at least run.** These had not: every test that names a fixture asserts
on the MARKUP STRING, and the control branch each fixture exists to exercise --
``new DOMParser().parseFromString(html, "text/html")`` inside the shipped
script -- has no implementation in node, which has no ``DOMParser``. So the
line that makes a fixture a control is the one line nothing had executed.

**THIS SCRIPT IS THE ENGINE.** It attaches to a Chrome that is already running,
opens a tab of its own, navigates NOWHERE, and evaluates each shipped script
against its own fixture in a detached document. There are FIVE control paths,
not four: ``search_results`` ships two fixtures, one per reader.

## WHY A POSITIVE RUN IS NOT ENOUGH, AND WHAT ``--plant`` IS FOR

A driver that reports PASS for everything looks exactly like a working one when
every fixture happens to match. So each path carries a PLANTED DEFECT -- a
one-edit corruption of its own fixture that MUST turn the comparison red -- and
``--plant`` runs those instead of the clean fixtures. A path whose planted
variant still reports PASS is not a control; it is a check that cannot fail,
and this script is built to say so in that exact word.

The plant for ``company_root`` is the sharpest of the five and is the reason
this is worth a browser slot at all: it removes the ``visually-hidden`` class
from the screen-reader copy and nothing else. If the walk really steps over
that subtree in a real DOM, the reading moves from ELEVEN to FORTY-ONE. If the
number does not move, the accessible-copy exclusion -- the property the whole
module was built around -- has never worked outside a synthetic node list.

## BOUNDS

**ATTACH ONLY.** Refuses to run unless ``LINKEDIN_CDP_ATTACH`` is set, so it
cannot launch a second Chrome against the persistent profile.

**IT NAVIGATES NOWHERE.** No ``goto``, no url, no LinkedIn surface is loaded.
The tab it opens stays on the blank page the browser gave it; the only thing
that crosses into that page is a fixture string this package authored.

**READS ONLY.** Every call is one of the shipped ``read_*`` coroutines. Nothing
is pressed, filled, scrolled or submitted.

**EVERY FIXTURE IS SYNTHETIC.** No string evaluated here came off a page, and
the output of every path is integers plus this package's own literals.

USAGE::

    set LINKEDIN_CDP_ATTACH=1
    <python> scripts/_probe_control_paths_live.py
    <python> scripts/_probe_control_paths_live.py --plant
    <python> scripts/_probe_control_paths_live.py --out <path under _state>

Resolve ``<python>`` with the interpreter you are already running. Never
``REPO / "venv"``: ``venv/`` is gitignored and absent in every worktree.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import (  # noqa: E402
    anchors,
    collections_page,
    company_root,
    search_results,
)

#: The modules whose bytes decide what this run measured. Printed as hashes so
#: a result can be tied to the exact source that produced it, which is the
#: half a probe usually leaves out.
EXERCISED = (
    "linkedin_server/anchors.py",
    "linkedin_server/search_results.py",
    "linkedin_server/collections_page.py",
    "linkedin_server/company_root.py",
    "linkedin_server/dom.py",
)


def provenance() -> dict[str, Any]:
    """This run's git head and the sha256 of every module it exercises."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
    except Exception as exc:  # noqa: BLE001 - provenance is best effort
        head = "unavailable:" + type(exc).__name__
    shas: dict[str, str] = {}
    for relative in EXERCISED:
        path = REPO / relative
        try:
            shas[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception as exc:  # noqa: BLE001
            shas[relative] = "unavailable:" + type(exc).__name__
    return {"git_head": head, "sha256": shas}


# ---------------------------------------------------------------------------
# THE FIVE PATHS
# ---------------------------------------------------------------------------
#
# Each entry is (name, fixture callable, reader callable, expectation, plant).
# The reader is called as ``reader(page, html=fixture())`` -- the SHIPPED
# coroutine, never a copy -- and the expectation is the module's own written
# constant wherever one exists.


def _collections_expectation() -> dict[str, int]:
    """``collections_page``'s expectation -- SHIPPED as of 2026-09-21.

    **IT DID NOT SHIP ONE UNTIL THIS PROBE WENT LOOKING.** Of the four modules
    declaring a fixture, three wrote down what theirs must produce and this one
    did not, so it was the only control in the package that could not have
    failed even once something finally executed it. The first run of this probe
    derived an expectation here from the fixture's own docstring promise; the
    constant now lives beside the fixture where its siblings' do, and this
    function reads it rather than re-deriving it.

    **A DERIVED EXPECTATION IS A PREDICTION THE PROBE MAKES ABOUT ITSELF.** A
    shipped one is a prediction the MODULE makes, which is the one that can be
    contradicted by a future edit to the module.
    """
    return dict(collections_page.CONTROL_EXPECTATION)


def _plant_strip_hrefs(html: str) -> str:
    """Remove every href. A route classifier must stop classifying routes."""
    out: list[str] = []
    index = 0
    while index < len(html):
        start = html.find(' href="', index)
        if start == -1:
            out.append(html[index:])
            break
        out.append(html[index:start])
        end = html.find('"', start + 7)
        if end == -1:
            break
        index = end + 1
    return "".join(out)


def _plant_unbutton(html: str) -> str:
    """Turn every control into a plain span. A panel reader must see none."""
    return html.replace("<button", "<span").replace("</button>", "</span>")


def _plant_unhead(html: str) -> str:
    """Demote every heading to a plain span. A heading reader must see none."""
    return (
        html.replace("<h2>", "<span>")
        .replace("</h2>", "</span>")
        .replace("<section>", "<div>")
        .replace("</section>", "</div>")
    )


def _plant_unhide(html: str) -> str:
    """THE SHARPEST PLANT. Strip the screen-reader class and nothing else.

    ``company_root._CONTROL_TREE`` puts a SHORTER hidden copy carrying 41
    beside the visible 11. If the walk genuinely steps over a
    ``visually-hidden`` subtree in a real DOM, removing that one class name
    must move the published number from 11 to 41. If it does not move, the
    exclusion has never been exercised anywhere but in a synthetic node list.
    """
    return html.replace("class='visually-hidden'", "class='shown-instead'")


async def _read_anchors(page: Any, html: str) -> dict[str, Any]:
    reading = await anchors.read_anchors(page, html=html)
    return {
        "by_class": anchors.tally(reading["counts"])["by_class"],
        "denominators": {
            "anchors_seen": reading["anchors_seen"],
            "values_refused": reading["values_refused"],
        },
    }


async def _read_results(page: Any, html: str) -> dict[str, Any]:
    reading = await search_results.read_results(page, html=html)
    return {
        "by_class": search_results.tally(
            reading["counts"], queries_present=reading["queries_present"]
        )["by_kind"],
        "denominators": {
            "anchors_seen": reading["anchors_seen"],
            "queries_present": reading["queries_present"],
            "values_refused": reading["values_refused"],
        },
    }


async def _read_filters(page: Any, html: str) -> dict[str, Any]:
    reading = await search_results.read_filters(page, html=html)
    return {
        "by_class": search_results.tally_filters(reading["counts"])["by_term"],
        "denominators": {
            "controls_seen": reading["controls_seen"],
            "matched_controls": reading["matched_controls"],
            "unmatched_controls": reading["unmatched_controls"],
            "empty_labels": reading["empty_labels"],
            "values_refused": reading["values_refused"],
        },
    }


async def _read_collections(page: Any, html: str) -> dict[str, Any]:
    reading = await collections_page.read_collections(page, html=html)
    tally = collections_page.tally(reading["indices"], reading["cards"])
    return {
        "by_class": tally["by_term"],
        "denominators": {
            "headings_seen": reading["headings_seen"],
            "unmatched": tally.get("by_term", {}).get(
                collections_page.UNMATCHED, 0
            ),
            "values_refused": reading["values_refused"],
        },
    }


async def _read_company_root(page: Any, html: str) -> dict[str, Any]:
    reading = await company_root.read_company_root(page, html=html)
    counts = company_root.connection_counts(reading)
    by_kind = counts.get("by_kind", {})
    flat: dict[str, int] = {}
    for kind, verdict in by_kind.items():
        if not isinstance(verdict, dict):
            continue
        value = verdict.get("value")
        # -1 RATHER THAN None, so a kind that published no number cannot be
        # confused with one that published zero. The expectation table below
        # never predicts -1, so a refusal always disagrees loudly.
        flat[kind + ".value"] = value if isinstance(value, int) else -1
    return {
        "by_class": flat,
        "verdicts": {
            kind: {
                "state": verdict.get("state"),
                "value": verdict.get("value"),
                "numeral": verdict.get("numeral"),
            }
            for kind, verdict in by_kind.items()
            if isinstance(verdict, dict)
        },
        "denominators": {
            "elements_walked": counts.get("elements_walked", 0),
            "chunks_considered": counts.get("chunks_considered", 0),
            "hidden_subtrees_skipped": counts.get("hidden_subtrees_skipped", 0),
            "non_content_skipped": counts.get("non_content_skipped", 0),
            "matches_refused": counts.get("matches_refused", 0),
            "values_refused": reading.get("values_refused", 0),
        },
    }


def paths() -> tuple[dict[str, Any], ...]:
    """The five control paths, each with its own expectation and plant."""
    return (
        {
            "name": "anchors.control_fixture",
            "module": "linkedin_server/anchors.py",
            "script": "dom.ANCHOR_CLASSIFY_JS",
            "fixture": anchors.control_fixture,
            "reader": _read_anchors,
            "expectation": dict(anchors.CONTROL_EXPECTATION),
            "expectation_is": "shipped",
            "plant": _plant_strip_hrefs,
            "plant_is": "every href removed",
        },
        {
            "name": "search_results.control_fixture",
            "module": "linkedin_server/search_results.py",
            "script": "dom.SEARCH_RESULTS_JS",
            "fixture": search_results.control_fixture,
            "reader": _read_results,
            "expectation": dict(search_results.CONTROL_EXPECTATION),
            "expectation_is": "shipped",
            "plant": _plant_strip_hrefs,
            "plant_is": "every href removed",
        },
        {
            "name": "search_results.filter_control_fixture",
            "module": "linkedin_server/search_results.py",
            "script": "dom.FILTER_PANEL_JS",
            "fixture": search_results.filter_control_fixture,
            "reader": _read_filters,
            "expectation": dict(search_results.FILTER_CONTROL_EXPECTATION),
            "expectation_is": "shipped",
            "plant": _plant_unbutton,
            "plant_is": "every control demoted to a span",
        },
        {
            "name": "collections_page.control_fixture",
            "module": "linkedin_server/collections_page.py",
            "script": "dom.COLLECTION_GROUPINGS_JS",
            "fixture": collections_page.control_fixture,
            "reader": _read_collections,
            "expectation": _collections_expectation(),
            "expectation_is": "shipped",
            "plant": _plant_unhead,
            "plant_is": "every heading demoted to a span",
        },
        {
            "name": "company_root.control_fixture",
            "module": "linkedin_server/company_root.py",
            "script": "dom.COUNT_LINES_JS",
            "fixture": company_root.control_fixture,
            "reader": _read_company_root,
            "expectation": {
                "connections_at_organisation.value": 11,
                "connections_following_page.value": 1204,
            },
            "expectation_is": "shipped_via_control_expectations",
            "plant": _plant_unhide,
            "plant_is": "screen-reader class renamed, nothing else",
        },
    )


def compare(observed: dict[str, int], expected: dict[str, int]) -> dict[str, Any]:
    """Every expected key, observed against its prediction. INTEGERS ONLY."""
    rows: dict[str, Any] = {}
    agreed = 0
    for key, want in sorted(expected.items()):
        got = observed.get(key)
        ok = isinstance(got, int) and got == want
        agreed += 1 if ok else 0
        rows[key] = {"expected": want, "observed": got, "ok": ok}
    return {
        "rows": rows,
        "agreed": agreed,
        "of": len(expected),
        "verdict": "PASS" if agreed == len(expected) and expected else "FAIL",
    }


async def run(planted: bool) -> dict[str, Any]:
    """Drive all five paths in one attached tab. Navigates nowhere."""
    from linkedin_server.browser import BROWSER
    from linkedin_server.config import CDP_ATTACH

    if not CDP_ATTACH:
        raise SystemExit(
            "REFUSING TO RUN. Set LINKEDIN_CDP_ATTACH=1 first. Without it this "
            "would LAUNCH a second Chrome on the persistent profile, which "
            "corrupts it and costs a signed-in session only the operator can "
            "restore."
        )

    # A PROBE THAT EXITS WITHOUT TEARING DOWN LEAKS ITS TAB, and the leak is
    # not cosmetic: ``cdp_bridge.attach`` enumerates every open target during
    # its handshake, so each abandoned tab lengthens the NEXT probe's attach.
    # Measured 2026-09-21 -- five probe processes took this browser from 8
    # pages to 13, and the sixth attach then exceeded its timeout and returned
    # ``browser_unavailable`` eight times running on a loaded box. The failure
    # looked like a dead browser and was a full one.
    #
    # ``BROWSER.stop()`` in attach mode closes ONLY the tab this process
    # opened and drops the CDP connection. It never closes the operator's
    # context and never touches his windows.
    out: list[dict[str, Any]] = []
    try:
        out = await _drive(BROWSER, planted)
    finally:
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - teardown noise, never fatal
            print("teardown raised " + type(exc).__name__)
    return {"paths": out}


async def _drive(BROWSER: Any, planted: bool) -> list[dict[str, Any]]:
    async with BROWSER.session() as page:
        try:
            return await _classify(page, planted)
        finally:
            # CLOSE THE PAGE, NEVER THE CONTEXT. The context is the operator's
            # own signed-in Chrome; the page is the tab this process opened.
            # ``tests/test_a_probe_closes_its_own_tab.py`` counts the scripts
            # that do not, and it went from 39 to 42 on this wave's three
            # session-using probes -- the same leak that put an attach
            # handshake over its ceiling earlier in the day.
            if not page.is_closed():
                await page.close()


async def _classify(page: Any, planted: bool) -> list[dict[str, Any]]:
    """Every control path, against one already-open tab. NAVIGATES NOWHERE.

    The tab the attached browser handed us already has a JS context, which is
    the only thing a detached-document control needs. Loading a LinkedIn
    surface to run a synthetic fixture would spend a page load and put a real
    page's text one scope away from a probe that does not want to see one.
    """
    out: list[dict[str, Any]] = []
    for path in paths():
        clean = path["fixture"]()
        html = path["plant"](clean) if planted else clean
        row: dict[str, Any] = {
            "name": path["name"],
            "module": path["module"],
            "script": path["script"],
            "fixture_chars": len(clean),
            "mode": "planted" if planted else "clean",
            "plant": path["plant_is"] if planted else None,
            "expectation_is": path["expectation_is"],
            "fixture_changed_by_plant": (html != clean) if planted else None,
        }
        try:
            reading = await path["reader"](page, html)
        except Exception as exc:  # noqa: BLE001
            # THE TYPE AND NEVER THE MESSAGE. An exception out of a page can
            # quote what it refused, and this package has already put a value
            # into a transcript that way once.
            row["ran"] = False
            row["error_type"] = type(exc).__name__
            row["comparison"] = {"verdict": "ERROR", "agreed": 0, "of": 0}
            out.append(row)
            continue
        row["ran"] = True
        row["denominators"] = reading["denominators"]
        if "verdicts" in reading:
            row["verdicts"] = reading["verdicts"]
        row["comparison"] = compare(reading["by_class"], path["expectation"])
        out.append(row)
    return out


def summarise(result: dict[str, Any], planted: bool) -> int:
    """Print the table. Returns the process exit code."""
    rows = result["paths"]
    print("")
    print("CONTROL PATHS DRIVEN THROUGH A REAL JS ENGINE")
    print("mode: " + ("PLANTED DEFECT" if planted else "CLEAN FIXTURE"))
    print("-" * 78)
    for row in rows:
        comparison = row["comparison"]
        print(
            "%-42s %-7s %2d/%-2d  %s"
            % (
                row["name"],
                comparison["verdict"],
                comparison["agreed"],
                comparison["of"],
                row["script"],
            )
        )
        if row.get("denominators"):
            print("    denominators: " + json.dumps(row["denominators"], sort_keys=True))
        if row.get("verdicts"):
            print("    verdicts:     " + json.dumps(row["verdicts"], sort_keys=True))
        misses = {
            key: cell
            for key, cell in comparison.get("rows", {}).items()
            if not cell["ok"]
        }
        if misses:
            print("    disagreed:    " + json.dumps(misses, sort_keys=True))
    print("-" * 78)

    if planted:
        # A PLANTED RUN INVERTS THE SCORE. Every path must go RED, and a path
        # that stays green under its own corruption is a check that cannot
        # fail -- which is the thing this repository has spent two days
        # counting and must never be reported as a pass.
        still_green = [
            row["name"] for row in rows if row["comparison"]["verdict"] == "PASS"
        ]
        if still_green:
            print("CANNOT FAIL: " + ", ".join(still_green))
            print("These paths reported PASS on a corrupted fixture.")
            return 1
        print("all %d paths went RED under their planted defect." % len(rows))
        return 0

    failed = [row["name"] for row in rows if row["comparison"]["verdict"] != "PASS"]
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1
    print("all %d control paths PASSED against their own expectations." % len(rows))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--plant",
        action="store_true",
        help="corrupt each fixture; every path MUST then go red",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="where to write the json (defaults under the gitignored _state/)",
    )
    args = parser.parse_args()

    destination = Path(
        args.out
        or (
            REPO
            / "_state"
            / ("control-paths-%s.json" % ("planted" if args.plant else "clean"))
        )
    )

    result = asyncio.run(run(args.plant))
    result["provenance"] = provenance()
    result["planted"] = args.plant
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    code = summarise(result, args.plant)
    print("")
    print("git head:  " + str(result["provenance"]["git_head"]))
    for relative, digest in sorted(result["provenance"]["sha256"].items()):
        print("  %-42s %s" % (relative, digest[:16]))
    print("raw json:  " + destination.name + " (under the gitignored _state/)")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
