"""THE GROUPS AND EVENTS SEARCHES RETURN WHAT THEY FOUND -- as group and event
records, under the six mitigations, each shown failing.

THE RULINGS. ``D2-SEARCH-VERTICALS-WIDENED`` admitted the groups and events
search verticals and said "Each then needs a reader"; ``NAMES-AT-RUNTIME`` lets
a read return the items it finds -- a group or an event as its title and its
link -- held to the six ``PEOPLE-DATA-MITIGATIONS``. Census rows ``N 161`` and
``N 179``.

THE READERS are ``linkedin_server.search_vertical_results.read_group_results``
and ``read_event_results``, reached by ``linkedin_search_groups`` and
``linkedin_search_events``. Their docstring states what each capture draws.

THE FIXTURES are ``tests/fixtures/synthetic/search_groups_live.html`` and
``search_events_live.html``: each capture's whole structure with declared
synthetic values (``tests/test_search_vertical_fixtures.py`` holds them to the
live lane's tracked copies). Each is well-formed XHTML, loaded through an XML
parser into a blank page, because an event result is a link holding a link,
which HTML's parser never builds (section 1 shows it losing them).

EVERY BROWSER HERE IS HEADLESS AND LOADS NOTHING: each page aborts every
network request, and no page is ever given an address.

    1  the readers over the fixtures, and the loader's necessity
    2  mitigation 1 -- declared fields only, and only the titles and hrefs read
    3  mitigation 2 -- sanitised and marked
    4  mitigation 3 -- never stored: failures by type; no module container
    5  mitigation 4 -- one page per call, and the cap
    6  mitigation 5 -- visible only
    7  mitigation 6 -- not a target by itself
    8  the drawings each rule refuses, counted
    9  the tools end to end
"""

from __future__ import annotations

import ast
import inspect
import logging
import re
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

import pytest
import pytest_asyncio

from linkedin_server import browser as browser_module
from linkedin_server import people_data, search_vertical_results as svr
from linkedin_server import server as server_module
from linkedin_server.config import logger as package_logger
from tests.plantedpage import PLANT, carries_the_plant, carries_the_plant_outside_records
from tests.test_a_people_reader_reads_one_page import PAGING_PARAMETERS
from tests.test_fixtures_hold_only_synthetic_people import is_reduced_to_shape

#: ONE BROWSER FOR THE MODULE, on the module's event loop. A launch per test
#: (``tests/test_writes.py``'s ``browser_page``) measured about ten seconds a
#: test on the loaded box of 2026-10-10 -- ten tests in 115 s -- past the
#: two-minute local gate. Every test still gets a FRESH CONTEXT, so nothing a
#: test draws or routes reaches the next.
IN_MODULE_LOOP = pytest.mark.asyncio(loop_scope="module")


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def _browser():
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


@pytest_asyncio.fixture(loop_scope="module")
async def browser_page(_browser):
    context = await _browser.new_context()
    try:
        yield await context.new_page()
    finally:
        await context.close()

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "tests" / "fixtures" / "synthetic"
READER_SOURCE = REPO / "linkedin_server" / "search_vertical_results.py"
XHTML = "{http://www.w3.org/1999/xhtml}"
TEXT = {
    "groups": (FIXTURES / "search_groups_live.html").read_text(encoding="ascii"),
    "events": (FIXTURES / "search_events_live.html").read_text(encoding="ascii"),
}
READERS = {"groups": svr.read_group_results, "events": svr.read_event_results}
VERTICALS = ("groups", "events")

#: The ids the fixtures draw, in order: the builder's declared synthetic runs.
GROUP_IDS = ("10001", "10002", "1000003", "1000004", "1000005", "10006", "10007",
             "1000008", "10000009")
EVENT_IDS = tuple("1" + str(n).zfill(18) for n in range(1, 14))
LINKS = {
    "groups": [f"https://www.linkedin.com/groups/{i}/" for i in GROUP_IDS],
    "events": [f"https://www.linkedin.com/events/{i}/" for i in EVENT_IDS],
}

#: Imports a fixture through an XML parser, keeping each link-in-a-link.
LOADER = """(xml) => {
  const doc = new DOMParser().parseFromString(xml, 'application/xhtml+xml');
  if (doc.getElementsByTagName('parsererror').length) return -1;
  const body = doc.getElementsByTagName('body')[0];
  document.body.replaceChildren(
    ...Array.from(body.childNodes).map((node) => document.importNode(node, true)));
  return document.querySelectorAll('a a').length;
}"""


async def _load(page: Any, vertical: str, *, mutate: str = "", via_html_parser: bool = False,
                text: Optional[str] = None) -> None:
    """The fixture in a blank page, every request aborted, then ``mutate``."""

    async def _refuse(route: Any) -> None:
        await route.abort()

    await page.route("**/*", _refuse)
    text = TEXT[vertical] if text is None else text
    if via_html_parser:
        await page.set_content(text, wait_until="domcontentloaded")
    else:
        await page.set_content("<html><body></body></html>")
        nested = await page.evaluate(LOADER, text)
        assert nested >= 0, "the XML loader could not parse the fixture"
        if vertical == "events":
            assert nested == 13, nested
    if mutate:
        await page.evaluate(mutate)


async def _read(page: Any, vertical: str, **load: Any) -> dict[str, Any]:
    await _load(page, vertical, **load)
    return await READERS[vertical](page)


def _records(result: dict[str, Any], vertical: str) -> list[dict[str, Any]]:
    return result[vertical]


def _denominators(result: dict[str, Any], vertical: str) -> dict[str, Any]:
    return result[vertical + "_denominators"]


def _expected_titles(vertical: str) -> list[str]:
    """The titles the fixture draws, read with an XML parser: the first
    paragraph of each group's list item; each event card's inner link."""
    root = ET.fromstring(TEXT[vertical].split("\n", 1)[1])
    titles = []
    for anchor in root.iter(XHTML + "a"):
        href = anchor.get("href") or ""
        if vertical == "groups" and re.fullmatch(r"/groups/[0-9]+/", href):
            item = next(e for e in anchor.iter() if e.get("role") == "listitem")
            titles.append(" ".join("".join(next(item.iter(XHTML + "p")).itertext()).split()))
        if vertical == "events" and re.fullmatch(r"/events/[0-9]+/", href):
            inner = [a for a in anchor.iter(XHTML + "a") if a is not anchor]
            if inner:
                titles.append(" ".join("".join(inner[0].itertext()).split()))
    return titles


# ---------------------------------------------------------------------------
# 1. The readers over the fixtures, and the loader's necessity
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_the_reader_returns_each_result_as_a_record(vertical, browser_page):
    result = await _read(browser_page, vertical)
    records = _records(result, vertical)
    assert [r["link"] for r in records] == LINKS[vertical]
    assert [r["title"] for r in records] == _expected_titles(vertical)
    assert all(is_reduced_to_shape(r["title"]) and r["title"] for r in records)
    count = len(LINKS[vertical])
    assert _denominators(result, vertical) == {
        "result_cards_seen": count,
        "result_cards_attempted": count,
        "returned": count,
        "skipped": {reason: 0 for reason in (
            svr.GROUP_SKIP_REASONS if vertical == "groups" else svr.EVENT_SKIP_REASONS)},
        "failed": {},
    }


@IN_MODULE_LOOP
async def test_THIS_CONTROL_CAN_FAIL_the_html_parser_loses_the_event_cards(browser_page):
    """What ``set_content`` makes of the events fixture: the outer link closed
    at the inner one, so no event link holds another and the reader finds no
    card -- as it must on a page drawn differently."""
    result = await _read(browser_page, "events", via_html_parser=True)
    assert result["events"] == []
    assert result["events_denominators"]["result_cards_seen"] == 0


# ---------------------------------------------------------------------------
# 2. Mitigation 1 -- declared fields only, and only titles and hrefs are read
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_mitigation_1_every_record_is_exactly_a_title_record(vertical, browser_page):
    result = await _read(browser_page, vertical)
    assert set(result) == {vertical, vertical + "_denominators"}
    for record in _records(result, vertical):
        assert frozenset(record) == people_data.TITLE_SHAPE
        assert people_data.as_record(record) is not None
    flat = repr(_denominators(result, vertical))
    assert not re.search(r"[Xx]{3}", flat), "no page text in the denominators"


def _spy(monkeypatch: Any) -> dict[str, list]:
    """Every text a handle read returned, and every attribute NAME a handle
    read -- Playwright's own methods, spied."""
    playwright = pytest.importorskip("playwright.async_api")
    handle = playwright.ElementHandle
    log: dict[str, list] = {"texts": [], "attributes": []}
    inner, content, attribute = handle.inner_text, handle.text_content, handle.get_attribute

    async def inner_spy(self: Any, *args: Any, **kwargs: Any) -> Any:
        value = await inner(self, *args, **kwargs)
        log["texts"].append(value or "")
        return value

    async def content_spy(self: Any, *args: Any, **kwargs: Any) -> Any:
        value = await content(self, *args, **kwargs)
        log["texts"].append(value or "")
        return value

    async def attribute_spy(self: Any, name: str, *args: Any, **kwargs: Any) -> Any:
        log["attributes"].append(name)
        return await attribute(self, name, *args, **kwargs)

    monkeypatch.setattr(handle, "inner_text", inner_spy)
    monkeypatch.setattr(handle, "text_content", content_spy)
    monkeypatch.setattr(handle, "get_attribute", attribute_spy)
    return log


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_mitigation_1_only_titles_and_hrefs_are_read(vertical, browser_page, monkeypatch):
    """The member count, the description, the date and the attendee line never
    enter this process: every text a handle read is a title (or the empty
    text of a title's absent children), and the only attribute read is href."""
    await _load(browser_page, vertical)
    log = _spy(monkeypatch)
    result = await READERS[vertical](browser_page)
    titles = set(_expected_titles(vertical))
    assert len(_records(result, vertical)) == len(LINKS[vertical])
    assert {text for text in log["texts"] if text.strip()} <= titles
    assert set(log["attributes"]) == {"href"}


@IN_MODULE_LOOP
async def test_THIS_CONTROL_CAN_FAIL_a_reader_touching_the_description_is_seen(
    browser_page, monkeypatch
):
    original = svr._read_group_card

    async def nosy(card: Any) -> Any:
        description = await card.query_selector('[role="listitem"] div p span')
        await description.inner_text()
        return await original(card)

    monkeypatch.setattr(svr, "_read_group_card", nosy)
    await _load(browser_page, "groups")
    log = _spy(monkeypatch)
    await svr.read_group_results(browser_page)
    titles = set(_expected_titles("groups"))
    assert not {text for text in log["texts"] if text.strip()} <= titles


# ---------------------------------------------------------------------------
# 3. Mitigation 2 -- sanitised and marked
# ---------------------------------------------------------------------------

#: A title laced with a zero-width space, a right-to-left override, a
#: control character and a run of whitespace -- set as the FIRST result's
#: title text, which the page then draws.
_LACED = "Laced" + chr(0x200B) + " Example" + chr(0x202E) + "   Group" + chr(0x07) + " Title"
_LACE = {
    "groups": """(laced) => {
      const card = document.querySelector('a[href^="/groups/"]');
      card.querySelector('[role="listitem"] p').textContent = laced;
    }""",
    "events": """(laced) => {
      const card = document.querySelector('a[href^="/events/"]');
      card.querySelector('a[href^="/events/"]').textContent = laced;
    }""",
}


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_mitigation_2_a_laced_title_comes_back_inert_and_marked(vertical, browser_page):
    await _load(browser_page, vertical)
    await browser_page.evaluate(_LACE[vertical], _LACED)
    records = _records(await READERS[vertical](browser_page), vertical)
    first = records[0]
    assert first["title"] == "Laced Example Group Title"
    assert first["title"] == people_data.sanitise(first["title"], cap=people_data.CAPS["title"])
    assert first[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
    assert all(r[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE for r in records)


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_THIS_CONTROL_CAN_FAIL_the_page_really_drew_the_laced_title(vertical, browser_page):
    await _load(browser_page, vertical)
    await browser_page.evaluate(_LACE[vertical], _LACED)
    drawn = await browser_page.evaluate(
        "(word) => document.querySelector(`a[href^='/${word}/']`).textContent", vertical
    )
    assert chr(0x200B) in drawn and chr(0x202E) in drawn


# ---------------------------------------------------------------------------
# 4. Mitigation 3 -- never stored
# ---------------------------------------------------------------------------


class _RaisingHandle:
    """An element handle whose every read raises, quoting the plant."""

    async def _raise(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(f"the page said {PLANT}")

    get_attribute = inner_text = text_content = is_visible = _raise
    query_selector = query_selector_all = _raise


class _RaisingPage:
    """A page drawing four cards, every read of which raises."""

    def __init__(self, *, list_raises: bool = False) -> None:
        self.list_raises = list_raises

    def locator(self, *args: Any, **kwargs: Any) -> "_RaisingPage":
        return self

    async def element_handles(self) -> list[_RaisingHandle]:
        if self.list_raises:
            raise RuntimeError(f"the page said {PLANT}")
        return [_RaisingHandle() for _ in range(4)]


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
@pytest.mark.parametrize("list_raises, failed", [(False, 4), (True, 1)])
async def test_mitigation_3_a_failure_is_counted_by_its_type_and_never_quoted(
    caplog, vertical, list_raises, failed
):
    with caplog.at_level(logging.DEBUG), caplog.at_level(
        logging.DEBUG, logger=package_logger.name
    ):
        result = await READERS[vertical](_RaisingPage(list_raises=list_raises))
    assert _records(result, vertical) == []
    assert _denominators(result, vertical)["failed"] == {"RuntimeError": failed}
    assert not carries_the_plant(result)
    assert not any(PLANT in record.getMessage() for record in caplog.records)


def test_THIS_CONTROL_CAN_FAIL_the_raising_page_really_quotes_the_plant():
    import asyncio

    with pytest.raises(RuntimeError, match=PLANT):
        asyncio.run(_RaisingHandle().inner_text())


def test_mitigation_3_the_reader_writes_to_no_module_level_container():
    """No ``global``, no module-level mutable, and no function that reaches a
    module-level name to mutate it -- the record path holds no cache."""
    tree = ast.parse(READER_SOURCE.read_text(encoding="utf-8"))
    module_names = {
        target.id
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
        if isinstance(target, ast.Name)
    }
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.Global, ast.Nonlocal))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if isinstance(owner, ast.Name) and owner.id in module_names:
                assert node.func.attr not in {"append", "add", "update", "extend",
                                              "setdefault", "insert", "__setitem__"}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            assert not isinstance(node.value, (ast.List, ast.Dict, ast.Set)), ast.dump(node)


def test_mitigation_3_the_reader_imports_no_logger_file_or_cache():
    source = READER_SOURCE.read_text(encoding="utf-8")
    imported = {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported <= {"annotations", "Any", "Awaitable", "Callable", "people_data"}, imported


# ---------------------------------------------------------------------------
# 5. Mitigation 4 -- one page per call, and the cap
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_mitigation_4_one_call_reads_at_most_the_ceiling(vertical, browser_page, monkeypatch):
    """The ceiling, lowered below the fixture's results."""
    monkeypatch.setattr(svr, "MAX_RESULTS_READ", 2)
    denominators = _denominators(await _read(browser_page, vertical), vertical)
    assert (denominators["result_cards_seen"], denominators["result_cards_attempted"],
            denominators["returned"]) == (len(LINKS[vertical]), 2, 2)


def test_mitigation_4_the_ceiling_is_above_what_the_captures_drew():
    assert svr.MAX_RESULTS_READ > max(len(GROUP_IDS), len(EVENT_IDS))


@pytest.mark.parametrize("tool", ["linkedin_search_groups", "linkedin_search_events"])
def test_mitigation_4_the_tools_take_no_paging_parameter_and_are_people_tools(tool):
    params = set(inspect.signature(getattr(server_module, tool)).parameters)
    assert params == {"keywords"}
    assert not params & PAGING_PARAMETERS
    assert tool in people_data.PEOPLE_TOOLS


#: Every page or handle method that loads, presses, types, scrolls or runs a
#: script -- none of which a reader that reads one page may call.
_ACTS = frozenset({
    "goto", "reload", "go_back", "go_forward", "click", "dblclick", "press", "fill",
    "type", "check", "uncheck", "tap", "hover", "select_option", "set_input_files",
    "evaluate", "evaluate_handle", "dispatch_event", "scroll_into_view_if_needed",
    "focus", "wait_for_timeout",
})


def _acts_called(source: str) -> set[str]:
    return {
        node.func.attr
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and node.func.attr in _ACTS
    }


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_mitigation_4_the_reader_loads_presses_and_scrolls_nothing(vertical, browser_page):
    await _load(browser_page, vertical)
    navigations: list[str] = []
    browser_page.on("framenavigated", lambda frame: navigations.append("navigated"))
    await READERS[vertical](browser_page)
    assert navigations == []
    assert _acts_called(READER_SOURCE.read_text(encoding="utf-8")) == set()


def test_THIS_CONTROL_CAN_FAIL_the_act_walk_sees_a_planted_press():
    assert _acts_called("async def f(card):\n    await card.click()\n") == {"click"}


# ---------------------------------------------------------------------------
# 6. Mitigation 5 -- visible only
# ---------------------------------------------------------------------------

_HIDE_FIRST_CARD = {
    "groups": "() => { document.querySelector('a[href^=\"/groups/\"]').style.display = 'none'; }",
    "events": "() => { document.querySelector('a[href^=\"/events/\"]').style.display = 'none'; }",
}
_HIDE_FIRST_TITLE = {
    "groups": """() => { document.querySelector('a[href^="/groups/"] [role="listitem"] p')
                  .style.display = 'none'; }""",
    "events": """() => { document.querySelector('a[href^="/events/"] a[href^="/events/"]')
                  .style.display = 'none'; }""",
}


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_mitigation_5_an_invisible_card_is_not_read(vertical, browser_page, monkeypatch):
    await _load(browser_page, vertical, mutate=_HIDE_FIRST_CARD[vertical])
    log = _spy(monkeypatch)
    result = await READERS[vertical](browser_page)
    records = _records(result, vertical)
    assert [r["link"] for r in records] == LINKS[vertical][1:]
    assert _denominators(result, vertical)["skipped"]["not_visible"] == 1
    assert _expected_titles(vertical)[0] not in log["texts"]


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_mitigation_5_an_invisible_title_is_not_read(vertical, browser_page):
    result = await _read(browser_page, vertical, mutate=_HIDE_FIRST_TITLE[vertical])
    assert [r["link"] for r in _records(result, vertical)] == LINKS[vertical][1:]
    assert _denominators(result, vertical)["skipped"]["not_visible"] == 1


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_THIS_CONTROL_CAN_FAIL_the_hidden_card_is_still_in_the_page(vertical, browser_page):
    await _load(browser_page, vertical, mutate=_HIDE_FIRST_CARD[vertical])
    count = await browser_page.locator(
        svr.GROUP_RESULT_CARD if vertical == "groups" else svr.EVENT_RESULT_CARD
    ).count()
    assert count == len(LINKS[vertical])


# ---------------------------------------------------------------------------
# 7. Mitigation 6 -- not a target by itself
# ---------------------------------------------------------------------------


def _importers_of(module: str) -> list[str]:
    """Package modules that import ``module``, read off their syntax trees."""
    found = []
    for path in sorted((REPO / "linkedin_server").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module == "linkedin_server" and any(
                alias.name == module for alias in node.names
            ):
                found.append(path.name)
                break
    return found


def test_mitigation_6_only_the_server_reaches_the_reader_and_no_write_tool_names_it():
    assert _importers_of("search_vertical_results") == ["server.py"]
    tree = ast.parse((REPO / "linkedin_server" / "server.py").read_text(encoding="utf-8"))
    from tests.test_server_surface import SANCTIONED_WRITE_TOOLS

    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name in SANCTIONED_WRITE_TOOLS:
            assert "search_vertical_results" not in ast.unparse(node), node.name


def test_THIS_CONTROL_CAN_FAIL_the_importer_walk_finds_a_real_import():
    assert "server.py" in _importers_of("people_results")


# ---------------------------------------------------------------------------
# 8. The drawings each rule refuses, counted
# ---------------------------------------------------------------------------

#: A plain group link and a plain event link -- no list item, no inner link --
#: planted in the page's main column, titled with the plant.
_PLANT_NON_RESULTS = """(plant) => {
  const main = document.querySelector('main');
  const g = document.createElement('a');
  g.setAttribute('href', '/groups/4242424/');
  g.textContent = plant;
  const e = document.createElement('a');
  e.setAttribute('href', '/events/4242424242424242424/');
  e.textContent = plant;
  main.prepend(g, e);
}"""


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_a_planted_non_result_link_is_not_returned(vertical, browser_page):
    await _load(browser_page, vertical)
    await browser_page.evaluate(_PLANT_NON_RESULTS, PLANT)
    result = await READERS[vertical](browser_page)
    assert [r["link"] for r in _records(result, vertical)] == LINKS[vertical]
    assert not carries_the_plant(result)


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_THIS_CONTROL_CAN_FAIL_the_planted_link_is_drawn_and_visible(vertical, browser_page):
    await _load(browser_page, vertical)
    await browser_page.evaluate(_PLANT_NON_RESULTS, PLANT)
    assert await browser_page.get_by_text(PLANT).first.is_visible()


#: Move the FIRST card's link to another result's id the moment the reader
#: reads its first text -- a re-render landing mid-read.
_MOVE_FIRST = {
    "groups": """() => { document.querySelector('a[href^="/groups/"]')
                   .setAttribute('href', '/groups/10000009/'); }""",
    "events": """() => { const card = document.querySelector('a[href^="/events/"]');
                   card.setAttribute('href', '/events/1000000000000000013/');
                   card.querySelector('a[href^="/events/"]')
                     .setAttribute('href', '/events/1000000000000000013/'); }""",
}


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_a_link_that_moved_while_read_is_skipped_and_counted(
    vertical, browser_page, monkeypatch
):
    await _load(browser_page, vertical)
    playwright = pytest.importorskip("playwright.async_api")
    original = playwright.ElementHandle.inner_text
    fired: list[bool] = []

    async def mid_read(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not fired:
            fired.append(True)
            await browser_page.evaluate(_MOVE_FIRST[vertical])
        return await original(self, *args, **kwargs)

    monkeypatch.setattr(playwright.ElementHandle, "inner_text", mid_read)
    result = await READERS[vertical](browser_page)
    assert fired
    skipped = _denominators(result, vertical)["skipped"]
    assert skipped["changed_while_read"] == 1
    assert [r["link"] for r in _records(result, vertical)] == LINKS[vertical][1:]


_NEST_TITLE = {
    "groups": """() => { const p = document.querySelector('a[href^="/groups/"] [role="listitem"] p');
                   const s = document.createElement('span'); s.textContent = 'Xxxx';
                   p.appendChild(s); }""",
    "events": """() => { const a = document.querySelector('a[href^="/events/"] a[href^="/events/"]');
                   const s = document.createElement('span'); s.textContent = 'Xxxx';
                   a.appendChild(s); }""",
}


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_a_title_holding_nested_text_refuses_the_result(vertical, browser_page):
    result = await _read(browser_page, vertical, mutate=_NEST_TITLE[vertical])
    assert _denominators(result, vertical)["skipped"]["title_has_nested_text"] == 1
    assert [r["link"] for r in _records(result, vertical)] == LINKS[vertical][1:]


@IN_MODULE_LOOP
async def test_an_event_title_naming_another_event_is_refused(browser_page):
    mutate = """() => { document.querySelector('a[href^="/events/"] a[href^="/events/"]')
                   .setAttribute('href', '/events/1000000000000000013/'); }"""
    result = await _read(browser_page, "events", mutate=mutate)
    assert result["events_denominators"]["skipped"]["title_is_another_event"] == 1
    assert [r["link"] for r in result["events"]] == LINKS["events"][1:]


@IN_MODULE_LOOP
async def test_a_result_nested_in_another_is_refused_and_counted(browser_page):
    mutate = """() => {
      const cards = document.querySelectorAll('a[href^="/groups/"]');
      cards[0].querySelector('[role="listitem"]').appendChild(cards[1]);
    }"""
    result = await _read(browser_page, "groups", mutate=mutate)
    assert result["groups_denominators"]["skipped"]["inside_another_result"] == 1
    assert [r["link"] for r in result["groups"]] == [LINKS["groups"][0]] + LINKS["groups"][2:]


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_a_result_drawn_twice_is_returned_once(vertical, browser_page):
    mutate = f"""() => {{
      const card = document.querySelector('a[href^="/{vertical}/"]');
      card.parentElement.appendChild(card.cloneNode(true));
    }}"""
    result = await _read(browser_page, vertical, mutate=mutate)
    assert _denominators(result, vertical)["skipped"]["already_returned"] == 1
    assert [r["link"] for r in _records(result, vertical)] == LINKS[vertical]


# ---------------------------------------------------------------------------
# 9. The tools end to end
# ---------------------------------------------------------------------------


async def _drive_tool(page: Any, tool: str, keywords: str) -> dict[str, Any]:
    """The tool end to end over a loaded page: the session yields it, and every
    navigation lands where it was sent without loading anything -- counted."""
    calls: list[str] = []

    @asynccontextmanager
    async def fake_session(*args: Any, **more: Any):
        yield page

    async def fake_goto(target: Any, url: str, **more: Any) -> str:
        calls.append(url)
        return url

    original = browser_module.BROWSER.session, browser_module.BROWSER.goto
    browser_module.BROWSER.session = fake_session
    browser_module.BROWSER.goto = fake_goto
    try:
        envelope = await getattr(server_module, tool)(keywords)
    finally:
        browser_module.BROWSER.session, browser_module.BROWSER.goto = original
    envelope["_gotos"] = list(calls)
    return envelope


TOOLS = {"groups": "linkedin_search_groups", "events": "linkedin_search_events"}


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_the_tool_loads_one_composed_page_and_returns_the_records(vertical, browser_page):
    await _load(browser_page, vertical)
    envelope = await _drive_tool(browser_page, TOOLS[vertical], "example keyword")
    assert envelope["ok"] is True, envelope
    assert envelope["_gotos"] == [
        f"https://www.linkedin.com/search/results/{vertical}/?keywords=example+keyword"
    ]
    assert envelope["pages_loaded"] == 1
    assert envelope["landed_where_it_was_sent"] is True
    assert envelope["landed_on_the_vertical"] is True
    assert envelope["query_applied"] == {"keywords": 1}
    assert [r["link"] for r in envelope[vertical]] == LINKS[vertical]
    assert "example keyword" not in repr({k: v for k, v in envelope.items() if k != "_gotos"})


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_the_tool_carries_page_text_only_inside_records(vertical, browser_page):
    """The first title the page draws is the plant: the tool publishes it
    only inside a record."""
    await _load(browser_page, vertical)
    await browser_page.evaluate(_LACE[vertical], PLANT)
    envelope = await _drive_tool(browser_page, TOOLS[vertical], "example keyword")
    assert carries_the_plant(envelope)
    outside, records = carries_the_plant_outside_records(envelope)
    assert outside == [] and records == len(LINKS[vertical])


async def _refused_without_a_session(tool: str, keywords: str) -> tuple[dict[str, Any], list]:
    """The tool called with a session that records any opening and refuses
    it, so a refusal that let a session open is seen rather than run live."""
    calls: list[str] = []

    @asynccontextmanager
    async def no_session(*args: Any, **kwargs: Any):  # pragma: no cover - must not run
        calls.append("session")
        raise AssertionError("a refused search opened a session")
        yield None

    async def no_goto(*args: Any, **kwargs: Any) -> str:  # pragma: no cover - must not run
        calls.append("goto")
        raise AssertionError("a refused search navigated")

    original = browser_module.BROWSER.session, browser_module.BROWSER.goto
    browser_module.BROWSER.session, browser_module.BROWSER.goto = no_session, no_goto
    try:
        envelope = await getattr(server_module, tool)(keywords)
    finally:
        browser_module.BROWSER.session, browser_module.BROWSER.goto = original
    return envelope, calls


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
@pytest.mark.parametrize("keywords", ["", "   "])
async def test_the_tool_refuses_a_missing_keyword_before_any_page(vertical, keywords):
    envelope, calls = await _refused_without_a_session(TOOLS[vertical], keywords)
    assert envelope["ok"] is False and envelope["refused"] == "keywords_required"
    assert envelope["pages_loaded"] == 0 and calls == []


@IN_MODULE_LOOP
@pytest.mark.parametrize("vertical", VERTICALS)
async def test_a_keyword_the_read_boundary_refuses_loads_nothing(vertical):
    envelope, calls = await _refused_without_a_session(TOOLS[vertical], "password reset")
    assert envelope["ok"] is False
    assert envelope["error"] == "refused_by_the_read_boundary"
    assert envelope["pages_loaded"] == 0 and calls == []
    assert "password reset" not in repr(envelope)


def test_the_landing_verdict_is_closed_segment_equality():
    settled = server_module._settled_on_the_vertical
    assert settled("https://www.linkedin.com/search/results/groups/?keywords=x", "groups")
    assert not settled("https://www.linkedin.com/search/results/people/?keywords=x", "groups")
    assert not settled("https://www.linkedin.com/search/results/groupsx/", "groups")
    assert not settled("https://example.com/search/results/groups/", "groups")
    assert not settled("https://www.linkedin.com/login", "events")
