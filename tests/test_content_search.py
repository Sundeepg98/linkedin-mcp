"""THE CONTENT SEARCH RETURNS WHICH POSTS IT FOUND -- as post records, read
over live session 11's capture, under the six mitigations, each shown failing.

THE RULINGS. ``CONTENT-VERTICAL-NOT-ALL-RESULTS`` serves census row ``M C93``
by the content search vertical, admitted on its own exact line; post text
returns under ``THIRD-PARTY-TEXT-AT-RUNTIME``; ``NAMES-AT-RUNTIME`` lets a read
return the items it finds, held to the six ``PEOPLE-DATA-MITIGATIONS``.

THE READER is ``linkedin_server.content_search.read_content_results``, reached
by ``linkedin_search_content``. Its docstring states what the capture draws.

THE FIXTURE is ``tests/fixtures/live11/search_content_posts.html``: live
session 11's skeleton of one content search with its LinkedIn words measured
against the session key and its people and their words declared synthetic
(``scripts/_build_content_search_skeleton.py``). The base capture,
``tests/fixtures/live11/search_content.html``, every text reduced to ``x``, is
the control that shows the reader refuses what it cannot recognise.

EVERY BROWSER HERE IS HEADLESS AND LOADS NOTHING: each page aborts every
network request, and no page is ever given an address. Every name in this
file is synthetic.

    1  compose: the one address, from the keyword alone
    2  the reader over the capture
    3  the controls: what it refuses to read
    4  an uncorroborated zero raises
    5  the mitigations: declared fields, sanitised, visible only, nothing pressed
    6  the tool end to end
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

from linkedin_server import browser as browser_module
from linkedin_server import content_search as cs
from linkedin_server import people_data, readonly
from linkedin_server import server as server_module
from linkedin_server.config import logger as package_logger
from linkedin_server.errors import ExtractionFailedError
from tests.plantedpage import PLANT, carries_the_plant, carries_the_plant_outside_records

#: ONE BROWSER FOR THE MODULE, on the module's event loop; a fresh context per
#: test, so nothing a test draws or routes reaches the next (the house
#: pattern of ``tests/test_search_vertical_results.py``).
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
FIXTURES = REPO / "tests" / "fixtures" / "live11"
POSTS = (FIXTURES / "search_content_posts.html").read_text(encoding="ascii")
BASE = (FIXTURES / "search_content.html").read_text(encoding="ascii")

#: The builder's declared synthetic authors and slugs, in card order.
AUTHORS = ("Kai Example", "Juno Fixture", "Lea Sample")
LINKS = tuple(
    f"https://www.linkedin.com/in/{slug}/"
    for slug in ("kai-example-a1", "juno-example-b2", "lea-example-c3")
)
#: A hashtag no fixture draws, so a quoted-back keyword would be seen.
KEYWORD = "#needlekeyword"
URL = "https://www.linkedin.com/search/results/content/?keywords=%23needlekeyword"

#: Where the reader's own cards are found in a loaded page, for plants.
CARD = cs.CARDS


async def _load(page: Any, text: str = POSTS, mutate: str = "", arg: Any = None) -> None:
    """The fixture in a blank page, every request aborted, then ``mutate``."""

    async def _refuse(route: Any) -> None:
        await route.abort()

    await page.route("**/*", _refuse)
    await page.set_content(text, wait_until="domcontentloaded")
    if mutate:
        await page.evaluate(mutate, arg)


async def _read(page: Any, **load: Any) -> dict[str, Any]:
    await _load(page, **load)
    return await cs.read_content_results(page)


def _words_in_card(index: int) -> str:
    """The words the builder wrote into card ``index``, in document order."""
    start = POSTS.index("Example post words %d.1" % (index + 1))
    end = POSTS.index("more", POSTS.index("expandable-text-button", start))
    lines = [line.strip() for line in POSTS[start:end].split("\n")]
    words = [line for line in lines if line.startswith("Example post words")
             or line.startswith("#exampletopic")]
    return " ".join(words)


# ---------------------------------------------------------------------------
# 1. compose: the one address, from the keyword alone
# ---------------------------------------------------------------------------


def test_a_keyword_composes_the_one_admitted_address():
    composed = cs.compose("example keyword")
    assert composed == {
        "built": True,
        "url": "https://www.linkedin.com/search/results/content/?keywords=example+keyword",
        "applied": {"keywords": 1},
    }
    assert readonly.is_read_url(composed["url"])


def test_a_hashtag_is_a_keyword_sent_percent_encoded():
    composed = cs.compose(KEYWORD)
    assert composed["url"] == URL
    assert readonly.is_read_url(composed["url"])


@pytest.mark.parametrize("keywords", ["", "   ", None])
def test_a_missing_keyword_is_refused_and_never_quoted(keywords):
    composed = cs.compose(keywords)
    assert composed["built"] is False and composed["refused"] == "keywords_required"


def test_the_mixed_all_results_page_is_never_composed():
    """The hashtag links a card draws go to /search/results/all/, which the
    ruling keeps refused; nothing here composes it."""
    assert "/search/results/all/" not in cs.compose(KEYWORD)["url"]
    assert not readonly.is_read_url(
        "https://www.linkedin.com/search/results/all/?keywords=%23example"
    )


def test_the_landing_verdict_is_the_vertical_path():
    assert cs.landed_on_the_vertical(URL)
    assert cs.landed_on_the_vertical("https://www.linkedin.com/search/results/content?keywords=x")
    assert not cs.landed_on_the_vertical("https://www.linkedin.com/search/results/all/?keywords=x")
    assert not cs.landed_on_the_vertical("https://www.linkedin.com/search/results/contents/")
    assert not cs.landed_on_the_vertical("https://www.linkedin.com/login")


# ---------------------------------------------------------------------------
# 2. The reader over the capture
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_the_three_cards_come_back_as_post_records(browser_page):
    result = await _read(browser_page)
    posts = result["posts"]
    assert [p["author"]["name"] for p in posts] == list(AUTHORS)
    assert [p["author"]["link"] for p in posts] == list(LINKS)
    assert [p["author"]["degree"] for p in posts] == ["3rd+"] * 3
    assert [p["author"]["headline"] for p in posts] == [None] * 3
    assert [p["link"] for p in posts] == [None] * 3
    for index, post in enumerate(posts):
        assert post["text"] == _words_in_card(index)
        assert set(post) == people_data.POST_SHAPE
        assert set(post["author"]) == people_data.PERSON_SHAPE
        assert post[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
    assert result["posts_denominators"] == {
        "result_cards_seen": 3,
        "result_cards_attempted": 3,
        "returned": 3,
        "skipped": {reason: 0 for reason in cs.SKIP_REASONS},
        "failed": {},
        "more_controls_drawn": 3,
    }


@IN_MODULE_LOOP
async def test_the_more_controls_own_text_is_not_a_post_word(browser_page):
    """The box HOLDS its more control, so its text is the box's text too; it
    is cut from the end, and a card without the control keeps every word."""
    result = await _read(browser_page)
    assert all(not p["text"].endswith("more") for p in result["posts"])
    removed = await _read(browser_page, mutate=(
        "() => document.querySelectorAll('[data-testid=\"expandable-text-button\"]')"
        ".forEach((b) => b.remove())"
    ))
    assert [p["text"] for p in removed["posts"]] == [p["text"] for p in result["posts"]]
    assert removed["posts_denominators"]["more_controls_drawn"] == 0


# ---------------------------------------------------------------------------
# 3. The controls: what it refuses to read
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_THIS_CONTROL_CAN_FAIL_the_base_capture_draws_no_results_screen(browser_page):
    """THE SAME MARKUP WITH EVERY WORD AND HOOK REDUCED TO x: the screen's name
    is gone, so nothing on the page is a result card, and the reader raises
    instead of reporting zero posts."""
    await _load(browser_page, text=BASE)
    with pytest.raises(ExtractionFailedError) as caught:
        await cs.read_content_results(browser_page)
    assert str(caught.value) == cs.WHY_UNREADABLE["no_screen"]


@IN_MODULE_LOOP
async def test_a_card_whose_heading_is_not_a_post_is_skipped(browser_page):
    result = await _read(browser_page, mutate=(
        "(sel) => { const h = document.querySelector(sel + ' h2 span');"
        " h.textContent = 'Example heading'; }"
    ), arg=CARD)
    assert result["posts_denominators"]["skipped"]["not_a_post"] == 1
    assert [p["author"]["name"] for p in result["posts"]] == list(AUTHORS[1:])


@IN_MODULE_LOOP
async def test_a_second_words_box_is_refused_not_chosen(browser_page):
    result = await _read(browser_page, mutate=(
        "(sel) => { const card = document.querySelector(sel);"
        " const box = card.querySelector('[data-testid=\"expandable-text-box\"]');"
        " box.parentNode.appendChild(box.cloneNode(true)); }"
    ), arg=CARD)
    assert result["posts_denominators"]["skipped"]["not_one_words_box"] == 1
    assert len(result["posts"]) == 2


@IN_MODULE_LOOP
async def test_a_member_link_to_another_profile_outside_the_box_refuses_the_card(browser_page):
    """Every member link outside the words box must name the author: a card
    that names a second profile there is not one author's post."""
    result = await _read(browser_page, mutate=(
        "(sel) => { const card = document.querySelector(sel);"
        " const a = document.createElement('a');"
        " a.href = 'https://www.linkedin.com/in/morgan-example-d4/';"
        " a.textContent = 'Morgan Example'; card.appendChild(a); }"
    ), arg=CARD)
    assert result["posts_denominators"]["skipped"]["more_than_one_profile"] == 1
    assert [p["author"]["name"] for p in result["posts"]] == list(AUTHORS[1:])


@IN_MODULE_LOOP
async def test_a_mention_inside_the_box_is_not_an_author(browser_page):
    """A member mentioned in the words is inside the box: the card is still
    its author's, and the mention is not read as a person."""
    result = await _read(browser_page, mutate=(
        "(sel) => { const box = document.querySelector(sel + "
        " ' [data-testid=\"expandable-text-box\"]');"
        " const a = document.createElement('a');"
        " a.href = 'https://www.linkedin.com/in/morgan-example-d4/';"
        " a.textContent = 'Morgan Example'; box.prepend(a); }"
    ), arg=CARD)
    first = result["posts"][0]
    assert first["author"]["name"] == AUTHORS[0]
    assert first["text"].startswith("Morgan Example")
    assert result["posts_denominators"]["returned"] == 3


@IN_MODULE_LOOP
async def test_an_organisation_author_is_skipped_not_returned_as_a_person(browser_page):
    """A Page's post has no member author block: no record type carries it."""
    result = await _read(browser_page, mutate=(
        "(sel) => { const card = document.querySelector(sel);"
        " card.querySelectorAll('a[href*=\"/in/\"]').forEach((a) => {"
        " a.href = 'https://www.linkedin.com/company/example-page/'; }); }"
    ), arg=CARD)
    assert result["posts_denominators"]["skipped"]["not_one_author_block"] == 1
    assert [p["author"]["name"] for p in result["posts"]] == list(AUTHORS[1:])


# ---------------------------------------------------------------------------
# 4. An uncorroborated zero raises
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_a_results_screen_with_no_card_raises_rather_than_reports_zero(browser_page):
    await _load(browser_page, mutate=(
        "(sel) => document.querySelectorAll(sel).forEach((c) => c.remove())"
    ), arg=CARD)
    with pytest.raises(ExtractionFailedError) as caught:
        await cs.read_content_results(browser_page)
    assert str(caught.value) == cs.WHY_UNREADABLE["no_cards"]


@IN_MODULE_LOOP
async def test_cards_seen_and_none_returnable_is_a_reading_not_a_raise(browser_page):
    """Cards ARE drawn, so the zero is corroborated by the denominators: three
    seen, three skipped by name."""
    result = await _read(browser_page, mutate=(
        "(sel) => document.querySelectorAll(sel + ' h2 span')"
        ".forEach((s) => { s.textContent = 'Example heading'; })"
    ), arg=CARD)
    assert result["posts"] == []
    assert result["posts_denominators"]["result_cards_seen"] == 3
    assert result["posts_denominators"]["skipped"]["not_a_post"] == 3


# ---------------------------------------------------------------------------
# 5. The mitigations
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_page_text_leaves_only_inside_records(browser_page):
    result = await _read(browser_page, mutate=(
        "([sel, plant]) => { const card = document.querySelector(sel);"
        " card.querySelector('a[href*=\"/in/\"] p').textContent = plant;"
        " card.querySelector('[data-testid=\"expandable-text-box\"]')"
        ".prepend(document.createTextNode(plant + ' ')); }"
    ), arg=[CARD, PLANT])
    assert carries_the_plant(result)
    outside, records = carries_the_plant_outside_records(result)
    assert outside == [] and records >= 1


@IN_MODULE_LOOP
async def test_names_and_words_are_sanitised_and_capped(browser_page):
    long_words = "Example " * 500
    result = await _read(browser_page, mutate=(
        "([sel, words]) => { const card = document.querySelector(sel);"
        " card.querySelector('a[href*=\"/in/\"] p').textContent = 'Kai\\u202e Example\\u200b';"
        " card.querySelector('[data-testid=\"expandable-text-box\"]')"
        ".prepend(document.createTextNode(words)); }"
    ), arg=[CARD, long_words])
    first = result["posts"][0]
    assert first["author"]["name"] == "Kai Example"
    assert len(first["text"]) <= people_data.CAPS["text"]
    assert first["text"] == people_data.sanitise(first["text"], cap=people_data.CAPS["text"])


@IN_MODULE_LOOP
async def test_a_card_the_page_does_not_show_is_not_read(browser_page):
    result = await _read(browser_page, mutate=(
        "(sel) => { document.querySelector(sel).style.display = 'none'; }"
    ), arg=CARD)
    assert result["posts_denominators"]["skipped"]["not_visible"] == 1
    assert [p["author"]["name"] for p in result["posts"]] == list(AUTHORS[1:])


@IN_MODULE_LOOP
async def test_nothing_is_pressed_and_no_link_is_followed(browser_page):
    """Every control and link records a press; the reading leaves none."""
    await _load(browser_page, mutate=(
        "() => { window.__pressed = 0; document.querySelectorAll('button, a, [role=\"button\"]')"
        ".forEach((el) => el.addEventListener('click', (e) => {"
        " window.__pressed += 1; e.preventDefault(); }, true)); }"
    ))
    await cs.read_content_results(browser_page)
    assert await browser_page.evaluate("() => window.__pressed") == 0


@IN_MODULE_LOOP
async def test_no_log_record_carries_page_text(browser_page, caplog):
    caplog.set_level(logging.DEBUG, logger=package_logger.name)
    await _read(browser_page, mutate=(
        "([sel, plant]) => { document.querySelector(sel + ' a[href*=\"/in/\"] p')"
        ".textContent = plant; }"
    ), arg=[CARD, PLANT])
    assert all(PLANT not in record.getMessage() for record in caplog.records)


def test_the_module_keeps_no_container_and_reads_no_class():
    """Mitigation 3 (never stored) and the structural anchor: no module-level
    list, dict or set is mutated by a read, and no selector names a class."""
    for name in ("SCREEN", "CARDS", "HEADING", "WORDS_BOX", "MORE_CONTROL",
                 "MEMBER_LINKS", "PARAGRAPHS"):
        selector = getattr(cs, name)
        assert "." not in selector.replace(cs.SCREEN_NAME, ""), name
        assert "class" not in selector, name
    assert isinstance(cs.SKIP_REASONS, tuple)


# ---------------------------------------------------------------------------
# 6. The tool end to end
# ---------------------------------------------------------------------------


async def _drive_tool(page: Any, keywords: str) -> dict[str, Any]:
    """The tool over a loaded page: the session yields it, and every navigation
    lands where it was sent without loading anything -- counted."""
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
        envelope = await server_module.linkedin_search_content(keywords)
    finally:
        browser_module.BROWSER.session, browser_module.BROWSER.goto = original
    envelope["_gotos"] = list(calls)
    return envelope


@IN_MODULE_LOOP
async def test_the_tool_loads_one_composed_page_and_returns_the_records(browser_page):
    await _load(browser_page)
    envelope = await _drive_tool(browser_page, KEYWORD)
    assert envelope["ok"] is True, envelope
    assert envelope["_gotos"] == [URL]
    assert envelope["pages_loaded"] == 1
    assert envelope["landed_where_it_was_sent"] is True
    assert envelope["landed_on_the_vertical"] is True
    assert envelope["query_applied"] == {"keywords": 1}
    assert [p["author"]["name"] for p in envelope["posts"]] == list(AUTHORS)
    assert KEYWORD not in repr({k: v for k, v in envelope.items() if k != "_gotos"})


@IN_MODULE_LOOP
async def test_the_tool_reports_an_uncorroborated_zero_as_an_error(browser_page):
    await _load(browser_page, text=BASE)
    envelope = await _drive_tool(browser_page, KEYWORD)
    assert envelope.get("ok") is not True
    assert envelope["error"] == "extraction_failed"
    assert "posts" not in envelope


async def _refused_without_a_session(keywords: str) -> tuple[dict[str, Any], list]:
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
        envelope = await server_module.linkedin_search_content(keywords)
    finally:
        browser_module.BROWSER.session, browser_module.BROWSER.goto = original
    return envelope, calls


@IN_MODULE_LOOP
@pytest.mark.parametrize("keywords", ["", "   "])
async def test_the_tool_refuses_a_missing_keyword_before_any_page(keywords):
    envelope, calls = await _refused_without_a_session(keywords)
    assert envelope["ok"] is False and envelope["refused"] == "keywords_required"
    assert envelope["pages_loaded"] == 0 and calls == []


@IN_MODULE_LOOP
async def test_a_keyword_the_read_boundary_refuses_loads_nothing():
    envelope, calls = await _refused_without_a_session("password reset")
    assert envelope["ok"] is False
    assert envelope["error"] == "refused_by_the_read_boundary"
    assert envelope["pages_loaded"] == 0 and calls == []
    assert "password reset" not in repr(envelope)
