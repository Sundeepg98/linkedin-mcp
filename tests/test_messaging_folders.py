"""His Archived conversations, read through ONE folder switch and put back -- census ``M M28``.

WHAT IS BUILT (lane build-msg2, 2026-11-26), on ruling
``VIEW-SWITCH-PRESS-RESTORED`` and integration 4's queued order (the folder
press's ``readonly.SANCTIONED_MUTATIONS`` entry): the read
``linkedin_archived_conversations`` -- on the composer's list, the folder pill
opened, ``Archived`` chosen, the list read, the folder it wore chosen again,
and the list read again and compared with the list read before.

WHAT IS MEASURED AND WHAT IS NOT. Every world's MARKUP is live session 11's
own (load 39): the composer's list, the open dropdown's four choices and the
Archived view's list, cut out of their captures byte for byte
(``tests/messaging_folder_worlds.py``). What a choice does on the COMPOSER's
page is not measured -- the switch was captured on ``/messaging/`` -- and every
world names the behaviour it chooses.

NOTHING HERE REACHES LINKEDIN. Every page is set into a local headless
Chromium with every request refused; the address a page wears is a proxy's.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import messaging_folders as mf
from linkedin_server import readonly, server, shape, threads
from tests import messaging_folder_worlds as w
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

COMPOSE = threads.COMPOSE_URL
MODULE = Path(mf.__file__)


@pytest.fixture
async def page(browser_page):
    """The shared local browser's page, with EVERY request refused."""

    async def _refuse(route) -> None:
        await route.abort()

    await browser_page.route("**/*", _refuse)
    yield browser_page


async def _at(page, html: str, url: str = COMPOSE, **proxy: Any) -> w.AtAddress:
    await page.set_content(html, wait_until="domcontentloaded")
    return w.AtAddress(page, url, **proxy)


async def _witness(page) -> dict[str, Any]:
    return await page.evaluate("() => window.__presses")


def _rows(reading: dict[str, Any]) -> dict[str, Any]:
    """The row-level facts of a list reading, without its page-wide counts."""
    view = mf.view_of(reading)
    return {key: view[key] for key in ("rows_total", "rows_rendered", "rows_placeholder",
                                       "unread_positions")}


# ---------------------------------------------------------------------------
# 1. The selectors, on the captures themselves
# ---------------------------------------------------------------------------


async def test_the_pill_reads_as_measured_on_every_capture(page):
    """The three captures of load 39 and the composer's list, read by the
    module's own reader: one pill, its folder, its state, its choices."""
    expected = {
        "messaging_list.html": ("Focused", "false", 0),
        "messaging_guarded.html": ("Focused", "false", 0),
        "messaging_folder_open.html": ("Focused", "true", 4),
        "messaging_archived.html": ("Archived", "false", 0),
    }
    for name, (folder, expanded, choices) in expected.items():
        await page.set_content((w.LIVE11 / name).read_text(encoding="utf-8"),
                               wait_until="domcontentloaded")
        pill = await mf._read_pill(page)
        assert (pill["pills"], pill["folder"], pill["expanded"], pill["choices_drawn"]) == (
            1, folder, expanded, choices
        ), name


def test_the_four_folders_are_the_open_captures_own():
    assert w.CAPTURED_CHOICES == list(mf.FOLDERS)


def test_a_choice_selector_is_built_only_from_the_four():
    assert mf.choice_selector("Archived").startswith(mf.CONTENT + " >> role=button")
    for bad in ("Unread", "archived", 'Archived"] , *', ""):
        with pytest.raises(ValueError):
            mf.choice_selector(bad)


# ---------------------------------------------------------------------------
# 2. The switch, applied, read and put back
# ---------------------------------------------------------------------------


async def test_the_archived_list_is_read_and_the_folder_put_back(page):
    """The Archived list the switch reads is the ARCHIVED capture's own list,
    read by the shipped list reader; the pill wears Focused again, closed, and
    the list after equals the list before."""
    at = await _at(page, w.world())
    reading = await mf.read_archived(at)
    assert reading["switched"] is True
    assert reading["folder_restored"] is True and reading["view_matches"] is True
    assert reading["restored"] is True
    assert await _witness(page) == {"pill": 2, "choices": {"Archived": 1, "Focused": 1}}

    # The ROWS are the archived capture's own; the page-wide receipt counts
    # are not compared, because the capture is /messaging/, whose conversation
    # pane the composer's page does not draw.
    await page.set_content(w.ARCHIVED_PAGE, wait_until="domcontentloaded")
    direct = await threads.read_conversation_list(page)
    assert _rows(reading["archived"]) == _rows(direct)
    assert reading["archived"]["rows_total"] == 20

    result = mf.archived_result(reading, COMPOSE, include_names=False)
    assert result["ok"] is True and result["restored"] is True
    assert (result["folder_before"], result["folder_after"]) == ("Focused", "Focused")
    assert result["presses"] == 4
    assert result["archived"]["opened_a_conversation"]["opened"] is False
    assert result["archived"]["conversations_listed"] == 20
    for row in result["archived"]["rows"]:
        assert "with" not in row
        if row["rendered"]:
            assert row["name"] == shape.NAME_PLACEHOLDER


async def test_names_leave_only_as_people_records_on_the_opt_in(page):
    at = await _at(page, w.world())
    reading = await mf.read_archived(at, include_names=True)
    result = mf.archived_result(reading, COMPOSE, include_names=True)
    rendered = [row for row in result["archived"]["rows"] if row["rendered"]]
    assert rendered, "the archived capture renders rows"
    for row in rendered:
        assert "name" not in row and isinstance(row["with"], (dict, type(None)))


# ---------------------------------------------------------------------------
# 3. Refused before any press -- the page's own counter the witness
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "build,url",
    [
        (lambda: w.world(), "https://www.linkedin.com/messaging/"),
        (lambda: w.two_pill_world(), COMPOSE),
    ],
    ids=["not-the-composers-list", "two-pills"],
)
async def test_nothing_is_pressed_off_the_measured_shape(page, build, url):
    at = await _at(page, build(), url)
    reading = await mf.read_archived(at)
    assert await _witness(page) == {"pill": 0, "choices": {}}
    assert reading["switched"] is False and reading["archived"] is None
    assert reading["steps"] == [] and reading["restore_steps"] == []
    assert mf.archived_result(reading, url, include_names=False)["ok"] is False


async def test_a_dropdown_already_open_is_not_pressed_into(page):
    at = await _at(page, w.world())
    await page.click(mf.PILL)  # THE TEST opens it; the module must not press
    reading = await mf.read_archived(at)
    assert await _witness(page) == {"pill": 1, "choices": {}}
    assert reading["switched"] is False and reading["steps"] == []


# ---------------------------------------------------------------------------
# 4. Every way the switch can go wrong reads as what it is
# ---------------------------------------------------------------------------


async def test_a_menu_without_archived_chooses_nothing_and_closes(page):
    """SHOWN FAILING: the measured choice removed from the menu."""
    at = await _at(page, w.world(drop=["Archived"]))
    reading = await mf.read_archived(at)
    assert await _witness(page) == {"pill": 2, "choices": {}}
    assert reading["steps"][0]["choice_drawn"] == 0
    assert reading["switched"] is False and reading["restored"] is True


async def test_a_choice_that_switches_nothing_is_not_an_empty_folder(page):
    at = await _at(page, w.world(noSwitch=True))
    reading = await mf.read_archived(at)
    assert reading["switched"] is False and reading["archived"] is None
    assert reading["restored"] is True
    assert "did not switch" in reading["why"]
    assert mf.archived_result(reading, COMPOSE, include_names=False)["ok"] is False


async def test_a_folder_that_will_not_go_back_is_the_loudest_answer(page):
    """SHOWN FAILING: the page keeps Archived whatever is chosen after it."""
    at = await _at(page, w.world(stuck=True))
    reading = await mf.read_archived(at)
    assert reading["switched"] is True
    assert reading["folder_restored"] is False and reading["restored"] is False
    assert reading["why"].startswith("THE FOLDER WAS NOT PUT BACK")
    result = mf.archived_result(reading, COMPOSE, include_names=False)
    assert result["ok"] is False and result["folder_after"] == "Archived"


async def test_a_list_that_comes_back_different_is_not_a_restore(page):
    """SHOWN FAILING: the pill reads Focused again, the list does not."""
    at = await _at(page, w.world(listDiffers=True))
    reading = await mf.read_archived(at)
    assert reading["folder_restored"] is True
    assert reading["view_matches"] is False and reading["restored"] is False
    assert "does NOT equal" in reading["why"]


async def test_a_switch_that_leaves_the_composer_is_not_a_restore(page):
    at = await _at(page, w.world(), leave_on="Archived",
                   leave_to="https://www.linkedin.com/messaging/thread/2-SYNTHETIC==/")
    reading = await mf.read_archived(at)
    assert reading["archived_on_the_composer"] is False
    assert reading["folder_restored"] is False and reading["restored"] is False


async def test_a_dropdown_a_choice_leaves_open_is_closed_by_its_own_pill(page):
    at = await _at(page, w.world(choiceStaysOpen=True))
    reading = await mf.read_archived(at)
    presses = await _witness(page)
    assert presses["choices"] == {"Archived": 1}
    assert reading["switched"] is False
    assert reading["restore_steps"] and reading["restore_steps"][0]["step"] == "close"
    assert (await mf._read_pill(page))["expanded"] == "false"
    assert reading["restored"] is True


# ---------------------------------------------------------------------------
# 5. The one mutation, and the tool
# ---------------------------------------------------------------------------


def test_activate_is_the_one_press_and_only_the_sequence_reaches_it():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef | ast.FunctionDef)}
    pressing = sorted(
        name for name, fn in functions.items()
        for call in ast.walk(fn)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
        and call.func.attr in {"click", "press", "fill", "type", "check", "tap", "dispatch_event"}
    )
    assert pressing == ["_activate"]
    callers = {
        name for name, fn in functions.items()
        for call in ast.walk(fn)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "_activate"
    }
    assert callers == {"_switch_to", "_close_if_open"}
    for helper in ("_switch_to", "_close_if_open"):
        reached_from = {
            name for name, fn in functions.items()
            for call in ast.walk(fn)
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == helper
        }
        assert reached_from <= {"read_archived", "_switch_to"}, (helper, reached_from)
    assert ("linkedin_server/messaging_folders.py", "_activate", "click") in readonly.SANCTIONED_MUTATIONS


class _Browser:
    """Stands where ``server.BROWSER`` stands: serves one world into the real
    local page and hands the tool a proxy wearing the address it landed on."""

    def __init__(self, page, html: str):
        self.page, self.html, self.gotos = page, html, []
        self.at: w.AtAddress | None = None

    def session(self):
        browser = self

        class _Session:
            async def __aenter__(self):
                browser.at = w.AtAddress(browser.page, "about:blank")
                return browser.at

            async def __aexit__(self, *exc):
                return False

        return _Session()

    async def goto(self, page, url: str) -> str:
        readonly.assert_read_url(url)
        self.gotos.append(url)
        await self.page.set_content(self.html, wait_until="domcontentloaded")
        page.url = url
        return url


async def test_the_tool_loads_one_page_and_returns_the_archived_rows(monkeypatch, page):
    fake = _Browser(page, w.world())
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_archived_conversations()
    assert fake.gotos == [COMPOSE]
    assert result["ok"] is True and result["pages_loaded"] == 1
    assert result["archived"]["conversations_listed"] == 20
    assert result["archived"]["names_included"] is False
    assert all(row["name"] == shape.NAME_PLACEHOLDER
               for row in result["archived"]["rows"] if row["rendered"])
