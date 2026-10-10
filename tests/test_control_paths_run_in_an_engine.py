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


# ---------------------------------------------------------------------------
# THE GROUP READER, over the live lane's tracked skeleton of a group's page
# ---------------------------------------------------------------------------
#
# ``group_page.read_group_page`` reads through ``anchors.read_anchors`` and has
# no control fixture of its own, and no test had run it in an engine. The live
# lane's session 2 captured one group's page and tracked its skeleton; the
# record of that load (``_audit/2026-09-23-live-lane-session-1.md``, "Live
# session 2") says what the live page gave: reach AMBIGUOUS, not one post
# permalink. Those two are the expectation, taken from the live load and not
# from this run.
#
# THE ANCHOR COUNT IS COMPARED WITH THE ENGINE'S OWN, NOT WITH THE RECORD'S 122.
# The skeleton's source holds 122 anchor tags, four of them opened inside an
# open anchor; a parser splits such nesting, so the engine's DOM holds 126. A
# live DOM can nest anchors, a serialised and re-parsed one cannot -- so the
# record's number is not the skeleton's, and the honest check is that the
# classifier saw every anchor the engine parsed.

GROUP_HOME = REPO / "tests" / "fixtures" / "live2" / "group_home.html"

#: A post permalink, planted as the control: the shape the reader counts as
#: reach. A five-digit id, under the identity sweep's six-digit floor.
PLANTED_PERMALINK = '<a href="/feed/update/urn:li:activity:12345/">x</a>'


async def _refuse(route) -> None:  # noqa: ANN001 - playwright route
    await route.abort()


async def _read_group(page, html: str):
    """THE SKELETON KEEPS ITS PIXELS' AND STYLESHEETS' ADDRESS SHAPES, so a
    browser loading it would fetch them: every request is refused in the
    page's own route first -- the network guard caught this test without it,
    as it caught the named-profile skeleton's."""
    from linkedin_server import group_page

    await page.route("**/*", _refuse)
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    out = await group_page.read_group_page(page)
    drawn = await page.evaluate("document.querySelectorAll('a').length")
    return out, group_page.reachability(out), drawn


async def test_the_group_reader_reads_the_live_lanes_group_page_in_an_engine(browser_page):
    html = GROUP_HOME.read_text(encoding="utf-8")
    assert "</main>" in html and "feed/update" not in html, (
        "the skeleton no longer has the shape this test rests on"
    )
    out, reach, drawn = await _read_group(browser_page, html)
    assert out["values_refused"] == 0, out
    assert out["anchors_seen"] == drawn > 0, (out["anchors_seen"], drawn)
    assert out["feed_update_anchors"] == 0, out
    assert reach["state"] == "ambiguous", reach


async def test_a_planted_post_permalink_moves_the_group_reader_off_ambiguous(browser_page):
    """THE CONTROL: one post permalink planted in the same page is counted, and
    the verdict leaves AMBIGUOUS -- so the clean test is not passing on a
    reader that counts nothing as reach."""
    html = GROUP_HOME.read_text(encoding="utf-8").replace(
        "</main>", PLANTED_PERMALINK + "</main>", 1
    )
    out, reach, drawn = await _read_group(browser_page, html)
    assert out["feed_update_anchors"] == 1, out
    assert out["anchors_seen"] == drawn, (out["anchors_seen"], drawn)
    assert reach["state"] != "ambiguous", reach
