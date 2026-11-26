"""linkedin_search_jobs reads the route LinkedIn SERVED, and an empty shortlist is never silent.

Lane search-fix26, 2026-11-26. LinkedIn is "gradually retiring classic job
search starting in September" (the banner over ``/jobs/search/``, measured on
three captures), and its replacement at ``/jobs/search-results/`` carries no
``/jobs/view/`` link at all. The shipped harvest keys on that link, the tool ran
it with ``allow_empty=True``, and nothing checked the landing -- so a redirect
to the AI page came back as ``results: []`` with a note blaming the filters.

WHAT IS HELD HERE, and which section holds it:

1. the landing is classified by whole path segments, and the AI landing must
   carry the keywords asked for;
2. the AI reader, on ``tests/fixtures/live11/jobs_search_ai.html`` -- built by
   ``scripts/_build_ai_job_search_skeleton.py`` from live session 11's raw
   capture, its structure LinkedIn's and every value replaced. Each neutral
   value sits in the slot of the field it stands for, so a reader bound to the
   wrong element returns the wrong neutral value, and the title's plain-span
   twin holds a NEEDLE (``Accessible Copy NN``) no row may return;
3. the shipped classic harvest keys NOTHING on that page, in a real Chromium
   -- the blindness the vetoes exist for, shown rather than cited;
4. the vetoes at the tool boundary: THE AI PAGE FED TO THE CLASSIC READER
   REFUSES, a classic zero refuses, an unreadable page refuses, and a landing
   on any other route refuses naming only its shape;
5. the fallback (``Q-SEARCH-ROUTE-POLICY``): keywords only, every other
   argument refused by name, one load and no re-query
   (``Q-FILTER-FIRES-SEARCH-CAP``);
6. the zero veto's vocabulary is empty and is shown able to speak;
7. the builder's own alphabet check passes the committed fixture and refuses a
   planted value.
"""
from __future__ import annotations

import importlib.util
import inspect
import re
from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import dom, job_search_route as route
from linkedin_server.server import linkedin_search_jobs
from tests.conftest import FakePage
from tests.test_sdui_surfaces_fixture import _with_html
from tests.test_tools import SEARCH_CARD, drive  # noqa: F401 - drive is used by injection

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "tests" / "fixtures"
AI_FIXTURE = FIXTURES / "live11" / "jobs_search_ai.html"
CLASSIC_FIXTURE = FIXTURES / "jobs_search.html"
BUILDER = REPO / "scripts" / "_build_ai_job_search_skeleton.py"

ASKED = "https://www.linkedin.com/jobs/search/?keywords=synthetic+role"
AI_LANDING = "https://www.linkedin.com/jobs/search-results/?keywords=synthetic+role"
KEYWORDS = "synthetic role"
SYNTHETIC_IDS = [str(4000000101 + n) for n in range(25)]
AGO = re.compile(r"^\d+ (?:second|minute|hour|day|week|month|year)s? ago$")


def _ai_html() -> str:
    return AI_FIXTURE.read_text(encoding="ascii")


def _builder():
    spec = importlib.util.spec_from_file_location("_build_ai_job_search_skeleton", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _MarkupPage(FakePage):
    """A FakePage that also answers ``page.content()``, as a real page does."""

    def __init__(self, *, html=None, **kwargs):
        super().__init__(**kwargs)
        self.html = html
        self.content_calls = 0

    async def content(self) -> str:
        self.content_calls += 1
        if self.html is None:
            raise RuntimeError("no markup")
        return self.html


# ---------------------------------------------------------------------------
# 1. The landing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www.linkedin.com/jobs/search/?keywords=a", route.CLASSIC),
        ("https://www.linkedin.com/jobs/search?keywords=a", route.CLASSIC),
        ("https://www.linkedin.com/jobs/search/?currentJobId=4000000101", route.CLASSIC),
        ("https://www.linkedin.com/jobs/search-results/?keywords=a", route.AI),
        ("https://linkedin.com/jobs/search-results/", route.AI),
        # Whole segments at fixed positions, never containment:
        ("https://www.linkedin.com/jobs/search-results/extra/", route.OTHER),
        ("https://www.linkedin.com/jobs/searchresults/", route.OTHER),
        ("https://www.linkedin.com/jobs/", route.OTHER),
        ("https://www.linkedin.com/jobs/collections/recommended/", route.OTHER),
        ("https://www.linkedin.com/search/results/jobs/", route.OTHER),
        ("https://www.example.com/jobs/search/", route.OTHER),
        ("not an address", route.OTHER),
        (None, route.OTHER),
    ],
)
def test_the_three_routes_are_told_apart_by_whole_segments(url, expected):
    assert route.landing_route(url) == expected


def test_every_route_literal_is_declared():
    assert set(route.ROUTES) == {route.CLASSIC, route.AI, route.OTHER}


@pytest.mark.parametrize(
    "url, keywords, expected",
    [
        (AI_LANDING, KEYWORDS, True),
        (AI_LANDING, "  Synthetic   ROLE ", True),
        (AI_LANDING, "another role", False),
        ("https://www.linkedin.com/jobs/search-results/", KEYWORDS, False),
        (AI_LANDING + "&keywords=synthetic+role", KEYWORDS, False),
        (AI_LANDING, "", False),
    ],
)
def test_the_ai_landing_must_carry_the_keywords_asked_for(url, keywords, expected):
    assert route.landed_query_matches(url, keywords) is expected


# ---------------------------------------------------------------------------
# 2. The AI reader, on the committed fixture
# ---------------------------------------------------------------------------


def test_the_fixture_is_the_ai_page_and_not_the_classic_one():
    evidence = route.render_evidence(_ai_html())
    assert evidence == {
        "html_read": True,
        "sdui_screen": "semantic_job_details",
        "ai_cards": 25,
        "job_view_anchors": 0,
        "classic_list": False,
        "deprecation_banner": False,
        "empty_state": None,
    }


def test_every_card_is_read_with_its_own_id():
    reading = route.read_ai_search(_ai_html())
    assert reading["cards"] == 25 and reading["unparsed"] == 0
    assert [row["job_id"] for row in reading["rows"]] == SYNTHETIC_IDS
    for row in reading["rows"]:
        assert row["url"] == "https://www.linkedin.com/jobs/view/" + row["job_id"]


def test_each_field_is_read_from_its_own_element():
    """The builder wrote each card's neutral values INTO THE FIELD'S OWN SLOT.

    So a title read from the company's paragraph comes back ``Company NN``, a
    place read positionally comes back as somebody else's number, and only a
    reader bound to the right element returns all three right on all 25.
    """
    rows = route.read_ai_search(_ai_html())["rows"]
    for number, row in enumerate(rows, start=1):
        assert row["title"] == "Role Title %02d" % number, row
        assert row["company"] == "Company %02d" % number, row
        assert re.fullmatch(
            r"Place %02d(?: \((?:Remote|Hybrid|On-site)\))?" % number, row["location"]
        ), row


def test_the_title_is_the_visible_copy_and_never_its_accessible_twin():
    html = _ai_html()
    # Not vacuous: the fixture carries the twins the needle is planted in.
    assert len(re.findall(r"Accessible Copy \d\d", html)) == 5
    rows = route.read_ai_search(html)["rows"]
    assert not [row for row in rows if "Accessible Copy" in (row["title"] or "")]


def test_easy_apply_is_the_cards_own_mark():
    rows = route.read_ai_search(_ai_html())["rows"]
    assert sum(1 for row in rows if row["easy_apply"] is True) == 8
    assert all(isinstance(row["easy_apply"], bool) for row in rows)


def test_the_posted_line_is_the_visible_age():
    rows = route.read_ai_search(_ai_html())["rows"]
    assert all(AGO.match(row["when"]) for row in rows), [row.get("when") for row in rows]


def test_the_workplace_is_one_of_three_literals():
    rows = route.read_ai_search(_ai_html())["rows"]
    workplaces = [row.get("workplace") for row in rows]
    assert sum(1 for value in workplaces if value) == 20
    assert {value for value in workplaces if value} <= {"remote", "hybrid", "on_site"}


def test_the_total_and_the_pager_are_telemetry_not_a_count():
    reading = route.read_ai_search(_ai_html())
    assert reading["total"] == {"shown": 99, "capped": True}
    assert reading["pager"] == {"indicators": 3, "next_control": "visible"}
    assert reading["easy_apply_toggle"] == {"drawn": True, "checked": False}


def test_a_card_without_its_title_wrapper_is_unparsed_not_guessed():
    html = _ai_html()
    first = html.index('componentkey="job-card-component-ref-4000000101"')
    marker = html.index('data-display-contents="true"', first)
    broken = html[:marker] + 'data-other="true"' + html[marker + len('data-display-contents="true"'):]
    reading = route.read_ai_search(broken)
    assert reading["unparsed"] == 1
    assert [row["job_id"] for row in reading["rows"]] == SYNTHETIC_IDS[1:]


def test_the_ai_reader_reads_nothing_off_the_classic_page():
    assert route.read_ai_search(CLASSIC_FIXTURE.read_text(encoding="utf-8"))["rows"] == []


def test_the_card_key_and_the_classic_anchor_match_the_shipped_patterns():
    assert route.JOB_VIEW_HREF.pattern == dom.JOB_HREF


# ---------------------------------------------------------------------------
# 3. The shipped classic harvest is blind to the AI page, in a real browser
# ---------------------------------------------------------------------------


async def test_the_shipped_harvest_keys_nothing_on_the_ai_page():
    async def work(page):
        return await dom.harvest_linked_cards(page, href_pattern=dom.JOB_HREF, max_items=75)

    assert await _with_html(_ai_html(), work) == []
    # THE CONTROL: the same harvest keys the classic fixture's cards.
    classic = await _with_html(CLASSIC_FIXTURE.read_text(encoding="utf-8"), work)
    assert len(classic) > 0


# ---------------------------------------------------------------------------
# 4. The vetoes, at the tool
# ---------------------------------------------------------------------------


async def test_the_ai_page_behind_the_classic_address_refuses_instead_of_returning_empty(drive):
    """THE RED. The AI page, fed to the classic reader, must REFUSE.

    The landing is the classic address -- the case the landing veto cannot
    see, a classic url serving the new page -- so the render veto alone stands
    between this read and an empty shortlist.
    """
    page = _MarkupPage(evaluate_result=[], html=_ai_html())
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS)

    assert result.get("error") == "extraction_failed", result
    assert "results" not in result and "count" not in result, result
    assert "25 AI result card(s)" in result["message"], result["message"]
    assert "SDUI screen semantic_job_details" in result["message"], result["message"]
    assert result["url"] == ASKED
    assert navigations == [ASKED]


async def test_the_ai_page_fed_to_the_real_classic_harvest_refuses(monkeypatch):
    """The same red with nothing faked but the navigation: the real harvest
    script, the real ``page.content()``, in a local Chromium."""
    result = await _tool_on_real_page(monkeypatch, _ai_html(), ASKED, keywords=KEYWORDS)
    assert result.get("error") == "extraction_failed", result
    assert "results" not in result
    assert "25 AI result card(s), 0 classic job link(s)" in result["message"], result["message"]


async def test_a_classic_zero_refuses_even_with_the_classic_list_drawn(drive):
    page = _MarkupPage(
        evaluate_result=[],
        html='<html><body><div class="scaffold-layout__list"><ul></ul></div></body></html>',
    )
    drive(page)

    result = await linkedin_search_jobs(keywords="cobol architect", start=500)

    assert result.get("error") == "extraction_failed", result
    assert "results" not in result
    assert "classic list drawn" in result["message"]
    assert "no empty state this package recognises" in result["message"]
    assert "offset is past the end" in result["message"]


async def test_a_page_whose_markup_cannot_be_read_refuses(drive):
    page = _MarkupPage(evaluate_result=[], html=None)
    drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS)

    assert result.get("error") == "extraction_failed", result
    assert "markup could not be read" in result["message"]


@pytest.mark.parametrize(
    "landing_url, fragments",
    [
        (
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4000000101",
            ("collections", "recommended", "4000000101"),
        ),
        ("https://www.linkedin.com/in/someone-planted-slug/", ("someone-planted-slug",)),
        ("https://www.example.com/jobs/search/", ("example",)),
    ],
)
async def test_a_landing_on_any_other_route_refuses_naming_only_its_shape(drive, landing_url, fragments):
    page = _MarkupPage(evaluate_result=[SEARCH_CARD], html=_ai_html())
    page.redirect_to = landing_url
    drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS)

    assert result.get("error") == "extraction_failed", result
    assert "results" not in result
    assert "described without its address" in result["message"]
    assert "characters, containing" in result["message"], "the shape must still be described"
    for fragment in fragments:
        assert fragment not in result["message"], fragment
    assert result["url"] == ASKED, "the field carries the asked-for address, never the landing"


async def test_a_classic_landing_with_cards_reads_as_it_always_did(drive):
    page = _MarkupPage(evaluate_result=[SEARCH_CARD], html=None)
    drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS)

    assert "error" not in result, result
    assert result["route"] == route.CLASSIC
    assert result["count"] == 1 and result["results"][0]["job_id"] == "4111222333"
    assert page.content_calls == 0, "a healthy read pays for no evidence"


# ---------------------------------------------------------------------------
# 5. The fallback (Q-SEARCH-ROUTE-POLICY, Q-FILTER-FIRES-SEARCH-CAP)
# ---------------------------------------------------------------------------


async def test_the_ai_fallback_returns_the_keyword_search_in_one_load(drive):
    page = _MarkupPage(evaluate_result=[], html=_ai_html())
    page.redirect_to = AI_LANDING
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS, limit=25)

    assert "error" not in result, result
    assert result["route"] == route.AI
    assert result["count"] == 25 and result["page_had"] == 25
    assert [row["job_id"] for row in result["results"]] == SYNTHETIC_IDS
    assert result["results_label"] == {"shown": 99, "capped": True}
    assert result["pager"] == {"indicators": 3, "next_control": "visible"}
    assert result["easy_apply_filter"] == {"drawn": True, "checked": False}
    # ONE LOAD, NO RE-QUERY: the fallback reads the page the request landed on.
    assert navigations == [ASKED]
    assert result["pages_loaded"] == 1
    assert "AI job search" in result["note"]


async def test_the_fallback_on_a_real_page(monkeypatch):
    result = await _tool_on_real_page(monkeypatch, _ai_html(), AI_LANDING, keywords=KEYWORDS)
    assert "error" not in result, result
    assert result["route"] == route.AI
    assert [row["job_id"] for row in result["results"]] == SYNTHETIC_IDS
    assert result["results"][0]["title"] == "Role Title 01"


#: One non-default value per argument the AI route refuses. Asserted to cover
#: the whole table below, so a refused argument with no case here fails.
REFUSED_CASES = {
    "location": {"location": "Planted Place"},
    "locations": {"locations": "Planted Place A; Planted Place B"},
    "remote": {"remote": "hybrid"},
    "date_posted": {"date_posted": "past_week"},
    "experience_level": {"experience_level": "mid_senior"},
    "job_type": {"job_type": "full_time"},
    "company_id": {"company_id": "5417062"},
    "easy_apply": {"easy_apply": True},
    "under_ten_applicants": {"under_ten_applicants": True},
    "in_your_network": {"in_your_network": True},
    "fair_chance_employer": {"fair_chance_employer": True},
    "sort_by": {"sort_by": "date"},
    "start": {"start": 7},
}


def test_every_refused_argument_has_a_case():
    assert set(REFUSED_CASES) == set(route.AI_ROUTE_UNMEASURED)


@pytest.mark.parametrize("argument", sorted(REFUSED_CASES))
async def test_every_unmeasured_filter_refuses_by_name_on_the_ai_route(drive, argument):
    page = _MarkupPage(evaluate_result=[], html=_ai_html())
    page.redirect_to = AI_LANDING
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS, **REFUSED_CASES[argument])

    assert result.get("error") == "extraction_failed", result
    assert "results" not in result, "never a shortlist that was not filtered"
    assert "Refused: " + argument in result["message"], result["message"]
    assert len(navigations) == 1, "a refusal costs no second load"
    for value in REFUSED_CASES[argument].values():
        if isinstance(value, str) and len(value) > 4:
            assert value not in result["message"], "the refusal names the argument, not its value"


async def test_the_easy_apply_refusal_reports_the_toggle_it_saw(drive):
    page = _MarkupPage(evaluate_result=[], html=_ai_html())
    page.redirect_to = AI_LANDING
    drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS, easy_apply=True)

    assert "Easy Apply toggle is drawn" in result["message"], result["message"]


async def test_an_ai_page_for_other_keywords_is_not_returned(drive):
    page = _MarkupPage(evaluate_result=[], html=_ai_html())
    page.redirect_to = "https://www.linkedin.com/jobs/search-results/?keywords=another+role"
    drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS)

    assert result.get("error") == "extraction_failed", result
    assert "does not carry the keywords" in result["message"]
    assert "another" not in result["message"]


async def test_an_ai_page_with_no_card_refuses(drive):
    html = re.sub(r'componentkey="job-card-component-ref-\d+"', 'componentkey="k0"', _ai_html())
    page = _MarkupPage(evaluate_result=[], html=html)
    page.redirect_to = AI_LANDING
    drive(page)

    result = await linkedin_search_jobs(keywords=KEYWORDS)

    assert result.get("error") == "extraction_failed", result
    assert "AI job search page held no job card" in result["message"]


def test_the_ai_route_table_covers_every_parameter_the_tool_takes():
    """A parameter added to the tool must be classified for the AI route."""
    params = set(inspect.signature(linkedin_search_jobs).parameters)
    classified = set(route.AI_ROUTE_HONOURED) | set(route.AI_ROUTE_UNMEASURED)
    assert params - {"limit"} == classified


def test_an_argument_at_its_default_is_never_named():
    assert route.ai_route_refusals() == []
    assert route.ai_route_refusals(remote=" ANY ", date_posted="Any", sort_by=" Relevance ") == []
    assert route.ai_route_refusals(start="0") == []


# ---------------------------------------------------------------------------
# 6. The zero veto's vocabulary
# ---------------------------------------------------------------------------


def test_no_empty_state_wording_is_declared_for_either_route():
    """EMPTY BECAUSE UNMEASURED. No capture shows either page with no results;
    a wording enters only with the capture that shows it."""
    assert route.CLASSIC_EMPTY_STATES == ()
    assert route.AI_EMPTY_STATES == ()


def test_a_declared_wording_would_be_believed():
    """THE CONTROL: the veto can speak. A planted vocabulary is believed; the
    same page with the shipped (empty) one is not."""
    html = "<html><body><main><p>Planted empty wording</p></main></body></html>"
    planted = route.render_evidence(html, empty_states=("Planted empty wording",))
    shipped = route.render_evidence(html, empty_states=route.empty_states_for(route.CLASSIC))
    assert route.zero_is_believable(planted) is True
    assert planted["empty_state"] == "Planted empty wording"
    assert route.zero_is_believable(shipped) is False


# ---------------------------------------------------------------------------
# 7. The builder's alphabet, over the committed fixture
# ---------------------------------------------------------------------------


def test_the_committed_fixture_passes_the_builders_alphabet():
    counts = _builder().verify(_ai_html())
    assert counts["output texts checked"] > 200 and counts["output attributes checked"] > 800


@pytest.mark.parametrize(
    "old, new",
    [
        ("Company 01", "Planted Needle Name"),
        ('aria-label="Dismiss x job"', 'aria-label="Dismiss Planted Needle job"'),
        ('href="#"', 'href="https://www.linkedin.com/in/someone-planted/"'),
        ("job-card-component-ref-4000000101", "job-card-component-ref-4987654321"),
        ("<img alt=\"\">", "<img alt=\"x\" data-member=\"planted\">"),
    ],
)
def test_the_alphabet_check_refuses_a_planted_value(old, new):
    html = _ai_html()
    assert old in html
    with pytest.raises(SystemExit):
        _builder().verify(html.replace(old, new, 1))


def test_the_fixture_is_ascii_and_carries_no_opaque_id():
    raw = AI_FIXTURE.read_bytes()
    raw.decode("ascii")
    text = raw.decode("ascii")
    assert not re.search(r"urn(?::|%3A)li(?::|%3A)", text, re.I)
    assert "ACoAA" not in text
    ids = set(re.findall(r"job-card-component-ref-(\d+)", text))
    assert ids == set(SYNTHETIC_IDS)


def test_the_fixture_passes_the_repositorys_fixture_privacy_patterns():
    """THE TOP-LEVEL GUARDS' PATTERNS, APPLIED BY NAME, BECAUSE THEIR GLOB DOES
    NOT REACH ``live11/``.

    ``test_sdui_surfaces_fixture.py`` runs its opaque-id and session-material
    checks over ``tests/fixtures/*.html`` only. This fixture sits in a
    per-session directory with its siblings, so the same two checks are run
    over it here with the patterns IMPORTED -- a second copy of a privacy
    pattern is a copy free to drift.
    """
    from tests.test_sdui_surfaces_fixture import _ALLOWED_OPAQUE_IDS, _OPAQUE_ID_PATTERNS

    html = AI_FIXTURE.read_text(encoding="utf-8")
    for token in ("li_at", "JSESSIONID", "csrfToken", "Bearer "):
        assert token not in html, token
    for label, pattern in _OPAQUE_ID_PATTERNS:
        for match in pattern.finditer(html):
            tail = html[match.start() : match.start() + 120]
            assert _ALLOWED_OPAQUE_IDS.search(tail), (label, tail[:90])
    # Not vacuous: the patterns do fire on a planted member id of the shape.
    # ASSEMBLED, NOT WRITTEN, so this file does not itself carry the shape
    # the repository-wide identity sweep hunts.
    planted = html + "urn" + ":li:" + "fsd_profile:" + "ACo" + "AA" + "PLANTED" * 4 + "0001"
    assert any(
        not _ALLOWED_OPAQUE_IDS.search(planted[m.start() : m.start() + 120])
        for _label, pattern in _OPAQUE_ID_PATTERNS
        for m in pattern.finditer(planted)
    )


# ---------------------------------------------------------------------------
# The real-browser harness
# ---------------------------------------------------------------------------


async def _tool_on_real_page(monkeypatch, html: str, landing_url: str, **kwargs):
    """Run ``linkedin_search_jobs`` over ONE local Chromium page holding ``html``.

    Only the navigation is faked: it sets the page's content and answers the
    landing given. The harvest script, ``page.content()`` and every reader run
    for real.
    """

    async def work(page):
        @asynccontextmanager
        async def session():
            yield page

        async def goto(target, url, **_kwargs):
            await target.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return landing_url

        monkeypatch.setattr(browser_module.BROWSER, "session", session)
        monkeypatch.setattr(browser_module.BROWSER, "goto", goto)
        return await linkedin_search_jobs(**kwargs)

    return await _with_html("<html><body></body></html>", work)
