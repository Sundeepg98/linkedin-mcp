"""The jobs home's recent-searches reader, run over real markup in a real page.

Census ``J 18`` -- recent searches: view and re-run. The fixture is a
sanitised copy of the LIVE capture of the ``/jobs/alerts/`` landing, built by
``scripts/_build_jobs_home_fixture.py``: every entry's structure, query-key set
and subtitle badge shape carried over, every query, place and query value
invented, and three decoys ADDED and marked. So these tests establish that the
reader is right about the shape LinkedIn drew on 2026-09-20; they cannot
establish that ``/jobs/jam/`` still draws it when opened directly, which is the
first live call's job.

WHY A BROWSER AND NOT A FAKE LOCATOR. The two defects this surface invites are
both about the DOM, not the Python: a selector aimed at the wrong list (the
page draws two under ONE element id), and ``inner_text`` reading a collapsed
entry as empty. A fake page returning canned strings would exercise neither.
``set_content`` loads local markup into a throwaway chromium -- never the
signed-in profile, which a live wave may hold.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

from linkedin_server import job_home

# NO MODULE-LEVEL UPPER-CASE CONSTANT beyond what pytest needs, deliberately:
# the impact gate couples every file that NAMES one defined here.


def _fixture_path() -> Path:
    return Path(__file__).parent / "fixtures" / "jobs_home_recent_searches.html"


def _html() -> str:
    return _fixture_path().read_text(encoding="ascii")


def _markup() -> str:
    """The fixture with its comments stripped: prose about a decoy is not one."""
    return re.sub(r"<!--.*?-->", "", _html(), flags=re.S)


async def _open(html: str, factory):
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded",
                                   timeout=60_000)
            return await factory(page)
        finally:
            await browser.close()


async def _read(html: str | None = None):
    async def factory(page):
        return await job_home.read_recent_searches(page)

    return await _open(_html() if html is None else html, factory)


def _entries_in_markup() -> list[str]:
    """History-tagged hrefs INSIDE main, by an independent parse."""
    inner = _markup().split("<main>", 1)[-1].split("</main>", 1)[0]
    return [h for h in re.findall(r'href="([^"]*)"', inner)
            if "/jobs/search-results/" in h
            and "origin=SEMANTIC_SEARCH_HISTORY" in h]


# ---------------------------------------------------------------------------
# 1. The fixture describes itself, so the numbers below are not transcriptions
# ---------------------------------------------------------------------------


def test_the_fixture_carries_six_entries_three_badges_and_its_three_decoys():
    markup = _markup()
    assert len(_entries_in_markup()) == 6
    assert markup.count("Alert On") == 3
    head = markup.split("<main>", 1)[0]
    assert "origin=SEMANTIC_SEARCH_HISTORY" in head, "decoy 1 (outside main) gone"
    assert "origin=JOBS_HOME_SEARCH_BUTTON" in markup, "decoy 2 (untagged) gone"
    assert markup.count('id="jobs-home-vertical-list__entity-list"') == 2, (
        "decoy 3 (a second list under the same id) gone")


def test_every_query_and_place_in_the_fixture_is_invented():
    """Nothing but placeholders where his queries and places were."""
    for query in re.findall(r"keywords=([^&\"]+)", _markup()):
        assert query.startswith(("Placeholder", "Decoy")), query
    for place in re.findall(r"Placeholder City [A-Z]", _markup()):
        assert re.fullmatch(r"Placeholder City [A-Z]", place)
    for value in re.findall(r"geoId=([0-9]+)", _markup()):
        assert value == "100000000"


# ---------------------------------------------------------------------------
# 2. The reading
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_reader_reads_the_six_entries_and_nothing_else():
    out = await _read()
    assert out["error"] is None and out["refusal"] is None
    assert out["list_label_seen"] is True
    assert out["entries_seen"] == 6
    # DECOY 2 is a search-route anchor inside main: scanned, and refused.
    # DECOY 1 is outside main and DECOY 3 is not the search route: not scanned.
    assert out["anchors_scanned"] == 7
    keywords = [e["search_keywords"] for e in out["searches"]]
    assert all(k.startswith("Placeholder") for k in keywords), keywords
    assert not any("Decoy" in k for k in keywords)
    assert [e["position"] for e in out["searches"]] == list(range(6))


@pytest.mark.asyncio
async def test_the_keywords_come_off_the_href_and_the_place_off_the_subtitle():
    out = await _read()
    hrefs = _entries_in_markup()
    for entry, href in zip(out["searches"], hrefs):
        expected = re.search(r"keywords=([^&]+)", href).group(1).replace("+", " ")
        assert entry["search_keywords"] == expected
    assert [e["location"] for e in out["searches"]] == [
        f"Placeholder City {c}" for c in "ABCDEF"]
    assert {e["location_state"] for e in out["searches"]} == {"read"}


@pytest.mark.asyncio
async def test_the_alert_badge_and_the_network_flag_discriminate():
    """Three of six carry the badge and one of six the network flag -- a
    reader defaulting either way would get one of these wrong."""
    out = await _read()
    assert [e["alert_on"] for e in out["searches"]] == [
        False, True, True, False, True, False]
    assert out["alerts_on"] == 3
    assert [e["in_your_network"] for e in out["searches"]] == [
        True, False, False, False, False, False]
    assert [e["workplace"] for e in out["searches"]] == [
        None, None, None, None, "remote", "remote"]


@pytest.mark.asyncio
async def test_facets_are_names_and_never_values():
    out = await _read()
    assert out["searches"][0]["facets"] == ["distance", "f_JIYN"]
    assert out["searches"][4]["facets"] == ["distance", "f_SAL"]
    text = repr(out)
    assert "f_SA_id_000" not in text, "a salary band VALUE was published"
    assert "100000000" not in text, "a place id was published"
    assert "search-results" not in text, "an href was published"


@pytest.mark.parametrize("rule, inner_text_drops_it", [
    # THE MODE THAT DISCRIMINATES: rendered, invisible, and ``inner_text``
    # returns "" -- a reader built on it reads the entry's badge as absent.
    ("visibility:hidden", True),
    # THE MODE THAT DOES NOT, kept so the file says why the first is needed:
    # an element inside a ``display:none`` subtree is not rendered, and
    # ``innerText`` then falls back to its full text. A test that tried only
    # this mode was run first and its control fired -- it could not have
    # caught a regression to ``inner_text``.
    ("display:none", False),
])
@pytest.mark.asyncio
async def test_collapsed_entries_are_read_however_they_are_hidden(
        rule, inner_text_drops_it):
    """THE LIVE-PAGE TRAP, PLANTED. Half the measured entries sit in
    LinkedIn's collapsed state, and the capture records the class, not how
    the stylesheet hides it. Hidden either way, the reading must not move --
    and the control measures what ``inner_text`` would have seen, so the
    discriminating variant cannot pass vacuously."""
    style = ("<style>.discovery-templates-vertical-list__list-item--collapsed"
             "{" + rule + "}</style>")
    hidden = _html().replace("<head>", "<head>" + style, 1)
    assert hidden != _html()

    async def factory(page):
        control = page.locator(
            ".discovery-templates-vertical-list__list-item--collapsed span")
        seen_by_inner_text = await control.last.inner_text()
        reading = await job_home.read_recent_searches(page)
        return seen_by_inner_text, reading

    seen_by_inner_text, out = await _open(hidden, factory)
    assert (seen_by_inner_text == "") is inner_text_drops_it, (
        rule, seen_by_inner_text)
    visible = await _read()
    assert out == visible


# ---------------------------------------------------------------------------
# 3. The zero that has two meanings
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_list_at_all_is_a_refusal_not_an_empty_history():
    out = await _read("<html><body><main><p>nothing</p></main></body></html>")
    assert out["entries_seen"] == 0
    assert out["list_label_seen"] is False
    assert out["refusal"] == "no_recent_search_list_drawn"


@pytest.mark.asyncio
async def test_a_drawn_but_empty_list_is_a_fact_about_him():
    html = ('<html><body><main><ul aria-label="Recent job searches"></ul>'
            "</main></body></html>")
    out = await _read(html)
    assert out["entries_seen"] == 0
    assert out["list_label_seen"] is True
    assert out["refusal"] is None


# ---------------------------------------------------------------------------
# 4. The pure entry parser
# ---------------------------------------------------------------------------

def _href(query: str) -> str:
    return "https://www.linkedin.com/jobs/search-results/?" + query


def test_an_entry_is_recognised_by_route_and_history_tag_only():
    tagged = "keywords=A&origin=SEMANTIC_SEARCH_HISTORY"
    assert job_home.recent_search_entry(_href(tagged), "Placeholder City A")
    assert job_home.recent_search_entry(
        _href("keywords=A&origin=OTHER"), "x") is None
    assert job_home.recent_search_entry(_href("keywords=A"), "x") is None
    assert job_home.recent_search_entry(
        "https://www.linkedin.com/jobs/search/?" + tagged, "x") is None
    assert job_home.recent_search_entry(None, "x") is None


def test_two_candidate_places_are_ambiguous_and_publish_no_string():
    entry = job_home.recent_search_entry(
        _href("keywords=A&origin=SEMANTIC_SEARCH_HISTORY"),
        "Placeholder City A \u00b7 Placeholder City B")
    assert entry["location"] is None
    assert entry["location_state"] == "ambiguous"


def test_a_badge_only_subtitle_is_absent_not_ambiguous():
    entry = job_home.recent_search_entry(
        _href("keywords=A&origin=SEMANTIC_SEARCH_HISTORY"), "Alert On")
    assert entry["location"] is None
    assert entry["location_state"] == "absent"
    assert entry["alert_on"] is True


def test_a_malformed_href_is_not_an_entry_and_does_not_raise():
    assert job_home.recent_search_entry("http://[::1", "x") is None


# ---------------------------------------------------------------------------
# 5. The alphabet, the failure path, and what the module may not do
# ---------------------------------------------------------------------------


def _strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v, f"{path}[]")


@pytest.mark.asyncio
async def test_only_his_two_inputs_leave_as_free_text():
    """Every published string is a literal of the module, except the two
    fields that ARE his inputs by contract."""
    out = await _read()
    alphabet = job_home.emitted_alphabet()
    for path, value in _strings(out):
        if path.endswith((".search_keywords", ".location")):
            continue
        assert value in alphabet, (path, value)


@pytest.mark.asyncio
async def test_an_exception_resets_every_field_and_publishes_only_a_type_name():
    class Exploding:
        def locator(self, _selector):
            raise RuntimeError("Placeholder City Q page string")

    out = await job_home.read_recent_searches(Exploding())
    assert out["error"] == "RuntimeError"
    assert "Placeholder" not in repr(out)
    assert out["searches"] == [] and out["entries_seen"] == 0
    assert out["list_label_seen"] is False


def test_the_module_navigates_nothing_and_takes_no_address():
    source = inspect.getsource(job_home)
    assert "goto(" not in source and "BROWSER" not in source
    assert list(inspect.signature(job_home.read_recent_searches).parameters) == [
        "page"]
    assert list(inspect.signature(job_home.recent_search_entry).parameters) == [
        "href", "subtitle"]


def test_the_home_is_admitted_and_the_route_it_lists_is_not():
    """The reader cannot become a route to the refused search page: the tool
    opens only the home, and the home's entries point at an address the
    boundary refuses."""
    from linkedin_server import readonly

    assert readonly.is_read_url(job_home.HOME_URL) is True
    assert readonly.is_read_url(
        "https://www.linkedin.com" + job_home.SEARCH_ROUTE
        + "?keywords=placeholder") is False
