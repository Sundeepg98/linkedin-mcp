"""Census row ``P L1``: his audience analytics, read over the capture's skeleton.

THE FIXTURE is ``tests/fixtures/live1/audience.html``, built by
``scripts/_build_audience_fixture.py`` from the live lane's session-1 capture of
``/analytics/creator/audience/``: the capture's STRUCTURE, the reader's UI words
verified by keyed hash, every value declared synthetic, the asides dropped.

WHAT IS HELD, each by a plant shown changing the verdict:

* the reading the first render draws -- the follower count, the view the nav's
  ``aria-current`` marks, six dimensions, one entry per dimension -- and every
  dimension's own list reported present-but-unread (no press);
* a person-name-shaped entry label comes back REDACTED, never verbatim;
* a RARE entry (a capitalised run drawn once) is redacted -- and the same label
  drawn twice is not, so the redactor is wired to the count and is not
  blanking everything;
* a dimension word this module does not know is COUNTED and never returned;
* a name planted in the ``aside`` (his profile card) never appears, and the
  reading is unchanged by it -- while the same block planted inside the
  demographics panel does change it;
* the tool loads exactly one admitted address and refuses an auth wall.

Every page variant is read in ONE browser launch and both tool drives in a
second: a launch costs seconds on a loaded box, a reading milliseconds.
"""
from __future__ import annotations

import asyncio
import functools
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import audience_analytics as aa
from linkedin_server import browser as browser_module
from linkedin_server import readonly
from linkedin_server import server as server_module
from linkedin_server.shape import CENSUS_REDACTED
from tests.plantedpage import PLANT, PageString

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "live1" / "audience.html"
HTML = FIXTURE.read_text(encoding="ascii").replace("\r\n", "\n")

#: The declared synthetic entries the builder planted, by dimension word.
SYNTHETIC = {
    "Industry": ("Example industry", 31),
    "Seniority": ("Example seniority", 24),
    "Job title": ("Example title", 9),
    "Location": ("Example location", 40),
    "Company size": ("Example size band", 18),
    "Company": ("Example Company Two", 3),
}
NAV_ORDER = ["Job title", "Location", "Seniority", "Company", "Industry", "Company size"]
ENTRY_ORDER = ["Industry", "Seniority", "Job title", "Location", "Company size", "Company"]
PLANT_WORDS = [w.casefold() for w in PLANT.split()]
UNKNOWN_WORD = "Example dimension"

#: An entry-shaped block carrying the plant, for the aside and panel plants.
PLANTED_BLOCK = (
    '<div><p>Industry</p><div><p>' + PLANT + '</p><p>50%</p></div>'
    '<div><svg role="progressbar"></svg></div></div>'
    '<a href="https://www.linkedin.com/in/exampleperson-markersurname/"><p>' + PLANT + '</p></a>'
)


def _with(*pairs: tuple[str, str]) -> str:
    text = HTML
    for old, new in pairs:
        assert text.count(old) >= 1, f"the fixture no longer draws {old!r}"
        text = text.replace(old, new)
    return text


def _current_on(word: str) -> str:
    """The fixture with ``aria-current`` moved from ``All`` to ``word``'s button."""
    text = _with((' aria-current="true"', ""))
    at = text.rindex("<button ", 0, text.index("\n" + word + "\n"))
    return text[:at] + '<button aria-current="true" ' + text[at + len("<button "):]


def _in_the_panel(block: str) -> str:
    """``block`` inserted as a sibling just before the panel's Industry entry."""
    second = HTML.index("\nIndustry\n", HTML.index("\nIndustry\n") + 1)
    entry = HTML.rindex("<div ", 0, HTML.rindex("<p ", 0, second))
    return HTML[:entry] + block + HTML[entry:]


#: Every page these tests read, by name.
PAGES: dict[str, str] = {
    "as_tracked": HTML,
    "name_as_label": _with(("\nExample title\n", "\n" + PLANT + "\n")),
    "rare_twice": _with(("\nExample industry\n", "\nExample Company Two\n")),
    "unknown_dimension": _with(("\nIndustry\n", "\n" + UNKNOWN_WORD + "\n")),
    "name_in_aside": HTML.replace("<aside></aside>", "<aside>" + PLANTED_BLOCK + "</aside>", 1),
    "name_in_panel": _in_the_panel(PLANTED_BLOCK),
    "view_on_location": _current_on("Location"),
    "view_unmarked": _with((' aria-current="true"', "")),
    "view_on_every_button": _with(("<button ", '<button aria-current="true" ')),
    "draws_none_of_it": "<!doctype html><html><body><main><p>x</p></main></body></html>",
}


def _carries_the_plant(value: Any) -> bool:
    flat = repr(value).casefold()
    return any(word in flat for word in PLANT_WORDS)


async def _session(pages: list[str], action: Any) -> list[Any]:
    """One local Chromium, every request aborted; ``action(page)`` per page."""
    playwright = pytest.importorskip("playwright.async_api")
    out = []
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            context = await browser.new_context()
            await context.route("**/*", lambda route: route.abort())
            page = await context.new_page()
            for html in pages:
                await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
                out.append(await action(page))
        finally:
            await browser.close()
    return out


@functools.lru_cache(maxsize=1)
def readings() -> dict[str, dict[str, Any]]:
    names = list(PAGES)
    outs = asyncio.run(_session([PAGES[n] for n in names], aa.read_audience_analytics))
    return dict(zip(names, outs))


# ---------------------------------------------------------------------------
# The pure half: no browser.
# ---------------------------------------------------------------------------


def test_a_word_that_leaves_is_the_module_s_own_constant_not_the_page_s():
    word = aa.classify(PageString("Job title"), aa.DIMENSIONS)
    assert word is aa.DIMENSIONS[0] and type(word) is str
    assert aa.classify(PageString(PLANT), aa.TAB_WORDS) is None
    assert aa.classify("  Company\n size ", aa.DIMENSIONS) == "Company size"


def test_the_follower_count_is_the_one_integer_beside_its_label():
    assert aa.parse_total("1,250\nTotal followers") == (1250, None)
    assert aa.parse_total("Total followers 87") == (87, None)
    assert aa.parse_total("Total followers") == (None, "not-an-integer")
    assert aa.parse_total("1,250 Total followers 3") == (None, "not-an-integer")
    assert aa.parse_total(PageString(PLANT)) == (None, "not-an-integer")


def test_a_share_pairs_with_its_label_by_shape_not_by_order():
    assert aa.pair(["Example title", "9%"]) == ("Example title", 9)
    assert aa.pair(["9%", "Example title"]) == ("Example title", 9)
    assert aa.pair(["9%", "8%"]) == (None, None)
    assert aa.pair(["Example title", "x"]) == (None, None)
    assert aa.pair(["101%", "Example title"]) == (None, None)


def test_a_name_shaped_label_drawn_once_is_redacted_and_drawn_twice_is_not():
    shaped, counts = aa.shape_labels([PLANT, "Example title"])
    assert shaped == [CENSUS_REDACTED, "Example title"] and counts["labels_redacted"] == 1
    # THE CONTROL: the count is wired. The same shape drawn twice is not rare.
    shaped, counts = aa.shape_labels([PLANT, PLANT])
    assert shaped == [PLANT, PLANT] and counts["labels_redacted"] == 0


# ---------------------------------------------------------------------------
# The reader over the capture's skeleton, in a local Chromium.
# ---------------------------------------------------------------------------


def test_the_first_render_reads_the_count_the_view_and_one_entry_per_dimension():
    out = readings()["as_tracked"]
    assert out["total_followers"] == 1250 and out["total_followers_why"] is None
    assert out["view"] == "All" and out["view_why"] is None
    assert out["dimensions"] == NAV_ORDER
    assert [e["dimension"] for e in out["entries"]] == ENTRY_ORDER
    for entry in out["entries"]:
        label, share = SYNTHETIC[entry["dimension"]]
        assert entry["share_percent"] == share, entry
        if entry["dimension"] == "Company":
            # THE PLANTED RARE ENTRY: a capitalised run drawn once.
            assert entry["label"] == CENSUS_REDACTED, entry
        else:
            assert entry["label"] == label, entry
    assert out["dimensions_drawn"] == list(aa.DIMENSIONS)
    assert out["dimensions_unread"] == []
    assert out["lists_unread"] == NAV_ORDER, "no press: every dimension's own list is unread"
    assert out["readable"] is True
    assert out["denominators"] == {
        "total_labels_seen": 1, "navs_matched": 1, "tabs_seen": 7, "tabs_unrecognised": 0,
        "progressbars_seen": 6, "entries_read": 6, "entries_unrecognised_dimension": 0,
        "entries_unpaired": 0, "labels_redacted": 1, "labels_opaque": 0, "labels_empty": 0,
    }


def test_a_person_name_planted_as_an_entry_label_comes_back_redacted():
    base, planted = readings()["as_tracked"], readings()["name_as_label"]
    assert not _carries_the_plant(planted), "the planted name left the reader"
    job = next(e for e in planted["entries"] if e["dimension"] == "Job title")
    assert job["label"] == CENSUS_REDACTED and job["share_percent"] == 9
    assert planted != base and planted["denominators"]["labels_redacted"] == 2


def test_a_rare_entry_is_redacted_and_the_same_label_drawn_twice_is_not():
    base, twice = readings()["as_tracked"], readings()["rare_twice"]
    rare = next(e for e in base["entries"] if e["dimension"] == "Company")
    assert rare["label"] == CENSUS_REDACTED
    # The verdict moves with the count: drawn twice, the shape is not rare.
    labels = {e["dimension"]: e["label"] for e in twice["entries"]}
    assert labels["Company"] == labels["Industry"] == "Example Company Two"
    assert twice["denominators"]["labels_redacted"] == 0


def test_a_dimension_word_this_module_does_not_know_is_counted_never_returned():
    base, out = readings()["as_tracked"], readings()["unknown_dimension"]
    assert UNKNOWN_WORD.casefold() not in repr(out).casefold()
    assert "Industry" not in out["dimensions"]
    assert [e["dimension"] for e in out["entries"]] == [d for d in ENTRY_ORDER if d != "Industry"]
    assert out["denominators"]["tabs_unrecognised"] == 1
    assert out["denominators"]["entries_unrecognised_dimension"] == 1
    assert base["denominators"]["tabs_unrecognised"] == 0


def test_a_name_in_the_aside_never_appears_and_changes_nothing():
    assert HTML.count("<aside></aside>") == 2, "the builder drops both asides to one stub each"
    base, beside, inside = (readings()[k] for k in ("as_tracked", "name_in_aside", "name_in_panel"))
    assert not _carries_the_plant(beside) and beside == base, "the aside is not read"
    # THE CONTROL: the same block inside the demographics panel IS read -- the
    # comparison above can see a change -- and its name still never leaves.
    assert inside != base and inside["denominators"]["entries_read"] == 7
    assert not _carries_the_plant(inside)


def test_a_page_that_draws_none_of_it_reads_empty_and_says_where():
    out = readings()["draws_none_of_it"]
    assert out["readable"] is False
    assert out["total_followers_why"] == "absent" and out["view_why"] == "no-demographics-nav"
    assert out["entries"] == [] and out["lists_unread"] == []
    assert set(out["denominators"].values()) == {0}


def test_the_view_is_the_tab_aria_current_marks_never_the_first():
    got = readings()
    assert got["as_tracked"]["view"] == "All"
    moved = got["view_on_location"]
    assert moved["view"] == "Location" and moved["view_why"] is None
    assert moved["lists_unread"] == [d for d in NAV_ORDER if d != "Location"]
    unmarked = got["view_unmarked"]
    assert unmarked["view"] is None and unmarked["view_why"] == "no-current-tab"
    assert unmarked["lists_unread"] == NAV_ORDER
    several = got["view_on_every_button"]
    assert several["view"] is None and several["view_why"] == "several-current-tabs"


# ---------------------------------------------------------------------------
# The tool: one admitted address, an auth wall refused.
# ---------------------------------------------------------------------------


@functools.lru_cache(maxsize=1)
def tool_drives() -> dict[str, dict[str, Any]]:
    """The tool end to end over the fixture, landing where it was sent and then
    on the login wall; each envelope carries its navigations under ``_gotos``."""
    results = {}

    async def drive(page: Any, land_on: str) -> dict[str, Any]:
        gotos: list[str] = []

        @asynccontextmanager
        async def fake_session(*args: Any, **more: Any):
            yield page

        async def fake_goto(target: Any, url: str, **more: Any) -> str:
            gotos.append(url)
            return land_on or url

        original = browser_module.BROWSER.session, browser_module.BROWSER.goto
        browser_module.BROWSER.session = fake_session
        browser_module.BROWSER.goto = fake_goto
        try:
            envelope = await server_module.linkedin_audience_analytics()
        finally:
            browser_module.BROWSER.session, browser_module.BROWSER.goto = original
        envelope["_gotos"] = gotos
        return envelope

    lands = {"served": "", "walled": "https://www.linkedin.com/login"}
    names = list(lands)
    pages = [HTML] * len(names)
    calls = iter(names)

    async def action(page: Any) -> dict[str, Any]:
        return await drive(page, lands[next(calls)])

    for name, envelope in zip(names, asyncio.run(_session(pages, action))):
        results[name] = envelope
    return results


def test_the_tool_loads_one_admitted_address_and_returns_the_reading():
    envelope = dict(tool_drives()["served"])
    assert envelope.pop("_gotos") == [aa.AUDIENCE_URL]
    assert readonly.is_read_url(aa.AUDIENCE_URL)
    assert envelope == readings()["as_tracked"]


def test_the_tool_refuses_an_auth_wall():
    envelope = tool_drives()["walled"]
    assert envelope.get("error") == "not_authenticated", envelope
    assert "entries" not in envelope and envelope["_gotos"] == [aa.AUDIENCE_URL]
