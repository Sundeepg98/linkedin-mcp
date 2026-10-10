"""Every control fixture in the package runs through a real JS engine, in the suite.

WHY THIS FILE EXISTS (2026-10-10, lane G2). The reader-leak guard stopped
counting a reader clean on what it hands back whatever a page draws, and four
of the readers it moved -- ``anchors.read_anchors``,
``collections_page.read_collections``, ``company_root.read_company_root`` and
the search readers -- turned out to have success paths NO TEST RAN IN ANY
ENGINE. Their readings are scripts this package runs in the page; the offline
guard's planted page answers every script with strings, and node has no
``DOMParser``. Each module ships a ``control_fixture()`` and a written
expectation for exactly this, and the only thing that ever ran them is
``scripts/_probe_control_paths_live.py`` -- attach-only, against the live
Chrome, by hand.

THIS RUNS THAT PROBE'S FIVE CONTROL PATHS IN A LOCAL HEADLESS CHROMIUM, on a
blank page, through the probe's own ``_classify`` -- the shipped reader each
time, called ``reader(page, html=fixture())``, and the module's own written
expectation. Nothing is copied: the paths, the expectations and the plants are
the probe's, so this file and the probe cannot drift apart. It navigates
nowhere and loads no LinkedIn surface; every fixture is synthetic.

AND EACH PATH IS SHOWN FAILING. The probe carries a one-edit planted defect
per path (every href removed, every control demoted, every heading demoted,
the screen-reader class renamed); each must change its fixture and turn its
comparison red, so a path that passes for any input is caught here.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import _probe_control_paths_live as probe  # noqa: E402

from tests.test_writes import browser_page  # noqa: E402,F401 -- a fixture

#: The five paths the probe declares. Pinned so a path removed from the probe
#: is a visible red here, not a silently smaller control set.
PATH_NAMES = (
    "anchors.control_fixture",
    "search_results.control_fixture",
    "search_results.filter_control_fixture",
    "collections_page.control_fixture",
    "company_root.control_fixture",
)


def test_the_probe_still_declares_the_five_paths():
    assert tuple(path["name"] for path in probe.paths()) == PATH_NAMES


async def test_every_control_fixture_reproduces_its_written_expectation(browser_page):
    """THE CLEAN RUN: each shipped reader, over its own fixture, in an engine,
    returns exactly what its module wrote down -- every key, integers only."""
    rows = await probe._classify(browser_page, planted=False)
    assert [row["name"] for row in rows] == list(PATH_NAMES)
    failed = {
        row["name"]: row.get("error_type") or row["comparison"]
        for row in rows
        if not row["ran"] or row["comparison"]["verdict"] != "PASS"
    }
    assert failed == {}, failed


async def test_every_planted_defect_turns_its_path_red(browser_page):
    """THE CONTROL: each path's one-edit corruption of its own fixture changes
    the fixture and makes the comparison disagree. A path that stays PASS here
    certifies nothing above."""
    rows = await probe._classify(browser_page, planted=True)
    assert [row["name"] for row in rows] == list(PATH_NAMES)
    unchanged = [row["name"] for row in rows if not row["fixture_changed_by_plant"]]
    assert unchanged == [], unchanged
    still_green = [
        row["name"] for row in rows
        if row["ran"] and row["comparison"]["verdict"] == "PASS"
    ]
    assert still_green == [], still_green
