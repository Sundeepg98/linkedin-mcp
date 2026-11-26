"""His scheduled posts, read behind the composer's Schedule button and closed -- census ``M C14``.

WHAT IS BUILT (lane build-msg2, 2026-11-26), on ruling
``SCHEDULED-LIST-AS-A-SHIPPED-READ``: the read ``linkedin_scheduled_posts`` --
the post composer opened EMPTY, Schedule post, View all scheduled posts, the
list read (zero only on the drawn empty headline), the modal closed on its own
Dismiss with nothing typed, and the composer loaded a second time and read
empty again; a stop on any autosave sign.

WHAT IS MEASURED AND WHAT IS NOT. Every world's MARKUP is live session 11's
own (load 25): the composer, the schedule dialog and the EMPTY list, with
LinkedIn's words put back by keyed shape (``tests/scheduled_posts_worlds.py``).
What Dismiss does, a populated list and a draft prompt are NOT measured: each
world that draws one names it.

NOTHING HERE REACHES LINKEDIN. Every page is set into a local headless
Chromium with every request refused.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import readonly, server
from linkedin_server import scheduled_posts as sp
from tests import scheduled_posts_worlds as w
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

MODULE = Path(sp.__file__)


@pytest.fixture
async def page(browser_page):
    """The shared local browser's page, with EVERY request refused."""

    async def _refuse(route) -> None:
        await route.abort()

    await browser_page.route("**/*", _refuse)
    yield browser_page


async def _witness(page) -> dict[str, Any]:
    return await page.evaluate("() => window.__presses")


# ---------------------------------------------------------------------------
# 1. The three states, read on the captures themselves
# ---------------------------------------------------------------------------


async def test_each_capture_reads_as_its_state(page):
    await page.set_content(w.COMPOSER_PAGE, wait_until="domcontentloaded")
    composer = await sp._read_state(page)
    assert sp.composer_empty(composer) and not sp.holds_text(composer)
    assert not sp.schedule_open(composer) and not sp.list_open(composer)

    await page.set_content(w.SCHEDULE_PAGE, wait_until="domcontentloaded")
    schedule = await sp._read_state(page)
    assert sp.schedule_open(schedule) and not sp.composer_empty(schedule)
    assert schedule["editors"] == 0 and schedule["view_all"] == 1

    await page.set_content(w.LIST_PAGE, wait_until="domcontentloaded")
    listed = await sp._read_state(page)
    assert sp.list_open(listed) and listed["empty_headline"] == 1
    assert not sp.schedule_open(listed)


# ---------------------------------------------------------------------------
# 2. The sequence
# ---------------------------------------------------------------------------


async def test_the_empty_list_reads_zero_and_the_composer_closes(page):
    await page.set_content(w.world(), wait_until="domcontentloaded")
    reading = await sp.read_scheduled(page)
    assert await _witness(page) == {"schedule": 1, "view_all": 1, "dismiss": 1, "other": 0}
    assert reading["list_read"] is True and reading["empty_headline_drawn"] is True
    assert reading["scheduled"] == 0
    assert reading["closed"] is True and reading["autosave_sign"] is None
    assert "zero scheduled posts" in reading["why"]


async def test_a_list_without_its_empty_headline_is_unknown_not_zero(page):
    """SHOWN FAILING: the empty headline taken away (a populated list -- a
    shape no capture holds) must not read as zero."""
    await page.set_content(w.world(listPopulated=True), wait_until="domcontentloaded")
    reading = await sp.read_scheduled(page)
    assert reading["list_read"] is True and reading["empty_headline_drawn"] is False
    assert reading["scheduled"] is None
    result = sp.scheduled_result(reading, {"empty": True}, {"closed": True, "steps": []})
    assert result["count_state"] == "unknown" and result["scheduled_posts"] is None


async def test_a_composer_holding_text_is_an_autosave_sign_and_nothing_is_pressed(page):
    """SHOWN FAILING: the composer opens holding words (the shape a kept draft
    might take): the sequence stops before its first press."""
    await page.set_content(w.world(startsWithText=True), wait_until="domcontentloaded")
    reading = await sp.read_scheduled(page)
    assert await _witness(page) == {"schedule": 0, "view_all": 0, "dismiss": 0, "other": 0}
    assert reading["autosave_sign"] == "the composer opened holding text"
    assert reading["why"].startswith("STOPPED ON AN AUTOSAVE SIGN")


@pytest.mark.parametrize("config", [{"dismissDrawsDialog": True}, {"dismissDrawsToast": True}],
                         ids=["a-dialog-after-dismiss", "a-toast-after-dismiss"])
async def test_anything_drawn_after_dismiss_stops_everything(page, config):
    """SHOWN FAILING: a prompt or a toast after the close is an autosave sign;
    nothing in it is pressed, and the result is not ok."""
    await page.set_content(w.world(**config), wait_until="domcontentloaded")
    reading = await sp.read_scheduled(page)
    presses = await _witness(page)
    assert presses["dismiss"] == 1 and presses["other"] == 0
    assert reading["closed"] is False
    assert reading["autosave_sign"] == "a dialog or a toast was drawn after Dismiss"
    result = sp.scheduled_result(reading, {"empty": True}, {"closed": True, "steps": []})
    assert result["ok"] is False and result["no_draft"] is False


async def test_a_schedule_dialog_that_never_opens_reads_no_list_and_still_closes(page):
    await page.set_content(w.world(noSchedule=True), wait_until="domcontentloaded")
    reading = await sp.read_scheduled(page)
    assert await _witness(page) == {"schedule": 1, "view_all": 0, "dismiss": 1, "other": 0}
    assert reading["list_read"] is False and reading["scheduled"] is None
    assert reading["closed"] is True


async def test_a_composer_that_will_not_close_is_said_loudly(page):
    await page.set_content(w.world(dismissDoesNothing=True), wait_until="domcontentloaded")
    reading = await sp.read_scheduled(page)
    assert reading["closed"] is False
    assert reading["autosave_sign"] == "the composer did not close on Dismiss"


async def test_off_the_measured_shape_nothing_is_pressed(page):
    """No composer on the page at all: nothing pressed, nothing claimed."""
    await page.set_content(w.LIST_PAGE.replace("share-box-v2__modal", "share-box-v2__other"),
                           wait_until="domcontentloaded")
    reading = await sp.read_scheduled(page)
    assert reading["steps"][-1]["pressed"] is False and len(reading["steps"]) == 1
    assert reading["list_read"] is False


def test_the_result_reports_no_draft_only_on_all_three_parts():
    reading = {"list_read": True, "scheduled": 0, "closed": True, "autosave_sign": None,
               "steps": [{"pressed": True}] * 3}
    good = sp.scheduled_result(reading, {"empty": True}, {"closed": True, "steps": [{"pressed": True}]})
    assert good["ok"] and good["no_draft"] and good["presses"] == 4 and good["pages_loaded"] == 2
    reopened_with_text = sp.scheduled_result(reading, {"empty": False, "holds_text": True},
                                             {"closed": None, "steps": []})
    assert not reopened_with_text["ok"] and not reopened_with_text["no_draft"]
    assert reopened_with_text["autosave_sign"] == "the composer reopened holding text"


# ---------------------------------------------------------------------------
# 3. The one press, and the tool
# ---------------------------------------------------------------------------


def test_press_is_the_one_mutating_call_and_types_nothing():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    functions = {node.name: node for node in ast.walk(tree)
                 if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))}
    pressing = sorted(
        name for name, fn in functions.items()
        for call in ast.walk(fn)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
        and call.func.attr in {"click", "press", "fill", "type", "check", "tap",
                               "dispatch_event", "set_input_files", "insert_text"}
    )
    assert pressing == ["_press"]
    callers = {
        name for name, fn in functions.items()
        for call in ast.walk(fn)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "_press"
    }
    assert callers == {"read_scheduled", "_close"}
    assert ("linkedin_server/scheduled_posts.py", "_press", "click") in readonly.SANCTIONED_MUTATIONS


class _Browser:
    """Stands where ``server.BROWSER`` stands: serves the world for every load
    of the composer into the real local page, and records each ask."""

    def __init__(self, page, html: str):
        self.page, self.html, self.gotos = page, html, []

    def session(self):
        browser = self

        class _Session:
            async def __aenter__(self):
                return browser.page

            async def __aexit__(self, *exc):
                return False

        return _Session()

    async def goto(self, page, url: str) -> str:
        readonly.assert_read_url(url)
        self.gotos.append(url)
        await page.set_content(self.html, wait_until="domcontentloaded")
        return url


async def test_the_tool_reads_zero_closes_and_finds_no_draft_on_the_second_load(monkeypatch, page):
    fake = _Browser(page, w.world())
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_scheduled_posts()
    assert fake.gotos == [sp.COMPOSER_URL, sp.COMPOSER_URL]
    assert result["ok"] is True and result["scheduled_posts"] == 0
    assert result["no_draft"] is True and result["reclosed"] is True
    assert result["presses"] == 4 and result["pages_loaded"] == 2


async def test_the_tool_does_not_load_again_after_an_autosave_sign(monkeypatch, page):
    fake = _Browser(page, w.world(startsWithText=True))
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_scheduled_posts()
    assert fake.gotos == [sp.COMPOSER_URL]
    assert result["ok"] is False and result["autosave_sign"] and result["presses"] == 0
