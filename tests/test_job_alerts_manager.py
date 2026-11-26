"""His job alerts off LinkedIn's alert manager -- census row ``J 37``, the LIST half.

Lane build-jobs2, 2026-11-26, over the live lane's session-11 capture of the
jobs home (load 17) with its heading measured by keyed shape
(``tests/fixtures/live11/jobs_alerts_manager_words.html``): outside ``main``,
the manager dialog headed ``Manage job alerts``, five alert rows, each an
anchor to the alert's own job search.

THE ALERTS' WORDS ARE HIS, so every one here is SYNTHETIC, planted into the
markup LinkedIn drew (HIS-OWN-TEXT-AT-RUNTIME: "fixtures synthetic"). They come
back as ``search_keywords``, through the tool-envelope guard's own-text door.

NOTHING HERE REACHES LINKEDIN: every load is ``set_content`` of a frozen world,
and every request a page would make is refused first.
"""
from __future__ import annotations

import inspect
import json
import re
from pathlib import Path

import pytest

from linkedin_server import job_alerts_manager as jam, server
from linkedin_server.errors import ExtractionFailedError
from tests.test_writes import browser_page  # noqa: F401 -- fixture

_LIVE11 = Path(__file__).parent / "fixtures" / "live11"
_WORDS = (_LIVE11 / "jobs_alerts_manager_words.html").read_text(encoding="ascii")
_REDUCED = (_LIVE11 / "jobs_alerts_manager.html").read_text(encoding="ascii")

#: Each row's search anchor, as drawn: the path and every value reduced to x.
_ANCHOR = re.compile(r'href="https://www\.linkedin\.com/jobs/x/\?keywords=x(&amp;[^"]*)"')

#: Synthetic queries, one per row, in page order -- invented words, never his.
_QUERIES = ("example role one", "example role two", "example role three",
            "example role four", "example role five")


def _planted(markup: str = _WORDS) -> str:
    """The capture with each row's keywords planted, in page order."""
    found = _ANCHOR.findall(markup)
    assert len(found) == 5, len(found)
    queries = iter(_QUERIES)

    def plant(match: "re.Match[str]") -> str:
        words = next(queries).replace(" ", "+")
        return f'href="https://www.linkedin.com/jobs/search/?keywords={words}{match.group(1)}"'

    return _ANCHOR.sub(plant, markup)


async def _refused(route) -> None:
    await route.abort()


async def _read(page, markup: str) -> dict:
    await page.set_content(markup, wait_until="domcontentloaded")
    return await jam.read_alert_manager(page)


async def test_the_five_alerts_are_read_off_the_manager_with_their_filters(browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    out = await _read(page, _planted())
    assert [a["search_keywords"] for a in out["alerts"]] == list(_QUERIES)
    assert [a["position"] for a in out["alerts"]] == [0, 1, 2, 3, 4]
    assert (out["rows_seen"], out["rows_without_a_search"], out["row_buttons"]) == (5, 0, 5)
    # The filters each search carries, by NAME only, as drawn: distance and
    # the place on every row, a date range on two, a salary on three.
    facets = [a["facets"] for a in out["alerts"]]
    assert all({"distance", "geoId"} <= set(f) for f in facets), facets
    assert sum("f_TPR" in f for f in facets) == 2 and sum("f_SAL" in f for f in facets) == 3, facets
    # No filter VALUE leaves -- the capture's values are x, and nothing of
    # the href but the planted keywords comes back.
    assert "geoId=" not in json.dumps(out)


async def test_THIS_CONTROL_CAN_FAIL_each_doubt_raises_or_is_counted(browser_page):
    """The heading is the anchor and a zero is never 'you have none'."""
    page = browser_page
    await page.route("**/*", _refused)
    # The reduced copy: the dialog's heading is x, so no manager is found.
    with pytest.raises(ExtractionFailedError):
        await _read(page, _planted(_REDUCED))
    # The capture as tracked: every href's keywords are x -- a search, read
    # as the query "x". The reader reads what the href holds; planting is
    # what makes the query a query.
    out = await _read(page, _WORDS)
    assert [a["search_keywords"] for a in out["alerts"]] == ["x"] * 5
    # A row whose anchor is not a job search is counted, never read.
    one_off = _planted().replace("https://www.linkedin.com/jobs/search/?keywords=example+role+two",
                                 "https://www.linkedin.com/feed/?keywords=example+role+two", 1)
    out = await _read(page, one_off)
    assert out["rows_without_a_search"] == 1 and len(out["alerts"]) == 4
    # A manager with no row that reads raises.
    start = _WORDS.index('<ul class="relative artdeco-list mt4">')
    end = _WORDS.index("</ul>", start)
    empty = _WORDS[:start] + '<ul class="relative artdeco-list mt4">\n' + _WORDS[end:]
    with pytest.raises(ExtractionFailedError):
        await _read(page, empty)
    # Two managers: neither is chosen.
    heading = "\nManage job alerts\n"
    assert _WORDS.count(heading) == 1
    twice = _WORDS.replace('<div id="kcc323291" aria-hidden="true">',
                           '<div role="dialog"><h2>Manage job alerts</h2></div>'
                           '<div id="kcc323291" aria-hidden="true">', 1)
    assert twice != _WORDS
    with pytest.raises(ExtractionFailedError):
        await _read(page, _planted(twice))


def test_an_alert_entry_is_a_job_search_or_nothing():
    assert jam.alert_entry("https://www.linkedin.com/jobs/search/?keywords=a+b&f_SAL=x") == {
        "search_keywords": "a b", "facets": ["f_SAL"]}
    for href in (None, "", "https://www.linkedin.com/feed/?keywords=a",
                 "https://www.linkedin.com/jobs/search/?distance=25", "::not a url"):
        assert jam.alert_entry(href) is None or jam.alert_entry(href)["search_keywords"] is None


def test_the_landing_must_keep_the_jobs_home():
    assert jam.landed_on_the_home("https://www.linkedin.com/jobs/jam/")
    assert jam.landed_on_the_home("https://www.linkedin.com/jobs/jam/?trk=x")
    for landed in ("https://www.linkedin.com/jobs/", "https://www.linkedin.com/jobs/jam/x",
                   "http://www.linkedin.com/jobs/jam/", None):
        assert not jam.landed_on_the_home(landed), landed


def test_the_tool_takes_nothing_and_holds_the_own_text_door():
    tool = getattr(server, "linkedin_job_alerts")
    assert list(inspect.signature(getattr(tool, "fn", tool)).parameters) == []
    from tests.test_tool_envelopes_emit_no_page_string import ADMITTED_OWN_TEXT, HIS_OWN_AUTHORED
    reason, scope = ADMITTED_OWN_TEXT["linkedin_job_alerts"]
    assert reason == HIS_OWN_AUTHORED and "search_keywords" in scope
