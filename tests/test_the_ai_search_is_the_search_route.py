"""The AI job search as the keyword search's OWN route, on session 12's two AI loads (lane jobs7).

Census rows ``J 1`` (the keyword search), ``J 20`` (the result card's fields,
the hiring chip among them) and ``J 40`` (proximity on a card). Live session
12's load 3 asked for the classic ``/jobs/search/`` and was REDIRECTED to the
AI search with no classic list (``C-SRCH-1``, the decision load); load 4
asked for the AI search's own address and was SERVED exactly (``C-SRCH-0b``).
So a call the AI route honours now ASKS FOR that address and reads it as its
route, instead of reaching it only through a redirect.

THE MARKUP IS SESSION 12'S OWN: ``tests/fixtures/live12/c_srch_1_words.html``
and ``c_srch_0b_words.html``, built by ``scripts/_build_jobs7_word_skeletons.py``
from the live lane's keyed skeletons -- the committed tracked copies, with
LinkedIn's words written only where their keyed shapes matched, and the card
and alert keys written by their grammar's shape, refused unless the card count
equals the session's own live reading (25 and 18). Every job's title, employer
and place stays ``x``, as in the tracked copy.

Nothing here reaches LinkedIn: the browser is a fake whose page answers
``content()`` with the fixture.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from linkedin_server import job_search_route as route
from linkedin_server import readonly, shape
from linkedin_server.server import linkedin_search_jobs
from tests.test_job_search_route import _MarkupPage
from tests.test_tools import SEARCH_CARD, drive  # noqa: F401 - drive is used by injection

REPO = Path(__file__).resolve().parent.parent
LIVE12 = REPO / "tests" / "fixtures" / "live12"
BUILDER = REPO / "scripts" / "_build_jobs7_word_skeletons.py"

KEYWORDS = "synthetic role"
AI_ASKED = "https://www.linkedin.com/jobs/search-results/?keywords=synthetic+role"
CLASSIC_PREFIX = "https://www.linkedin.com/jobs/search/?"

#: Session 12's own count of each load's AI cards (``_audit/2026-11-26-live-
#: session-12.md``, "E2 to E17": load 3 "25 AI cards", load 4 "18 AI cards"),
#: taken live by the shipped ``job_search_route.render_evidence``.
LIVE_CARDS = {"c_srch_1": 25, "c_srch_0b": 18}
FIRST_ID = {"c_srch_1": 4000000201, "c_srch_0b": 4000000301}

SYNTHETIC_CARD_KEY = re.compile(r"job-card-component-ref-4000000[23]\d\d")


def _builder():
    spec = importlib.util.spec_from_file_location("_build_jobs7_word_skeletons", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def words(stem: str) -> str:
    return (LIVE12 / (stem + "_words.html")).read_text(encoding="ascii")


def plain(stem: str) -> str:
    return (LIVE12 / (stem + ".html")).read_text(encoding="ascii")


def body_lines(text: str) -> list[str]:
    marker = "\n-->\n"
    assert marker in text, "a words fixture opens with its provenance comment"
    return text.split(marker, 1)[1].split("\n")


def plant(markup: str, old: str, new: str, count: int = 1) -> str:
    """An ASSERTED edit of the markup after the provenance comment."""
    head, sep, body = markup.partition("\n-->\n")
    assert body.count(old) == count, (body.count(old), count)
    return head + sep + body.replace(old, new)


def read(stem: str) -> dict:
    return route.read_ai_search(words(stem))


# ---------------------------------------------------------------------------
# 1. The fixtures are session 12's captures, plus declared words and keys only
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stem", sorted(LIVE_CARDS))
def test_each_words_fixture_differs_from_its_capture_only_by_declared_words_and_keys(stem):
    capture_stem, declared, _first, _alert = _builder().SPEC[stem + "_words"]
    assert capture_stem == stem
    fixture = body_lines(words(stem))
    capture = plain(stem).split("\n")[1:]
    assert len(fixture) == len(capture)
    differing = [(a, b) for a, b in zip(fixture, capture) if a != b]
    assert differing, "the fixture must carry something its capture does not"
    alert_key = _builder().ALERT_KEY_SYNTHETIC
    attribute = re.compile(r'([A-Za-z_:][-A-Za-z0-9_:.]*)="([^"]*)"')
    written_values: set[str] = set()
    for written, reduced in differing:
        if not written.startswith("<"):
            # A text line: the declared word, where the capture reads x.
            assert reduced == "x" and written in declared, (written[:60], reduced[:60])
            written_values.add(written)
            continue
        mine, theirs = attribute.findall(written), attribute.findall(reduced)
        assert [name for name, _ in mine] == [name for name, _ in theirs]
        assert attribute.sub("", written) == attribute.sub("", reduced)
        for (name, value), (_name, was) in zip(mine, theirs):
            if value == was:
                continue
            assert was == "x", (name, was)
            assert value in declared or value == alert_key or SYNTHETIC_CARD_KEY.fullmatch(value), name
            written_values.add(value)
    # Every declared word was written somewhere (the builder refuses otherwise).
    assert set(declared) <= written_values


@pytest.mark.parametrize("stem", sorted(LIVE_CARDS))
def test_the_cards_the_fixture_keys_are_the_cards_the_session_counted_live(stem):
    reading = read(stem)
    assert reading["cards"] == LIVE_CARDS[stem]
    ids = [row["job_id"] for row in reading["rows"]]
    assert ids == [str(FIRST_ID[stem] + n) for n in range(LIVE_CARDS[stem])]


# ---------------------------------------------------------------------------
# 2. The reader on session 12's markup
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stem", sorted(LIVE_CARDS))
def test_every_card_on_session_12s_page_is_read_with_every_field_its_slots_draw(stem):
    reading = read(stem)
    rows = reading["rows"]
    assert len(rows) == LIVE_CARDS[stem] and reading["unparsed"] == 0
    for row in rows:
        # The title, employer and place slots are drawn on every card; their
        # text is a third party's and stays reduced in a tracked file.
        assert (row["title"], row["company"], row["location"]) == ("x", "x", "x")
        assert row["url"] == "https://www.linkedin.com/jobs/view/" + row["job_id"]
        assert re.fullmatch(r"\d+ (?:second|minute|hour|day|week|month|year)s? ago", row["when"])
        assert row["easy_apply"] in (True, False)
    assert reading["sdui_screen"] == "semantic_job_details"


def test_the_page_telemetry_on_each_load_is_what_the_session_drew():
    first, second = read("c_srch_1"), read("c_srch_0b")
    assert first["total"] == {"shown": 99, "capped": True}
    assert second["total"] == {"shown": 18, "capped": False}
    assert first["pager"] == {"indicators": 3, "next_control": "visible"}
    assert second["pager"] == {"indicators": 1, "next_control": "hidden"}
    assert [sum(r["easy_apply"] for r in x["rows"]) for x in (first, second)] == [7, 14]
    assert first["easy_apply_toggle"] == second["easy_apply_toggle"] == {"drawn": True, "checked": False}


def test_the_hiring_chip_is_read_off_session_12s_cards():
    """RED BEFORE LANE JOBS7: the AI reader read no hiring chip at all."""
    first = [row.get("hiring") for row in read("c_srch_1")["rows"]]
    assert first.count(["actively_reviewing_applicants"]) == 5
    assert sum(1 for h in first if h) == 5
    second = [row.get("hiring") for row in read("c_srch_0b")["rows"]]
    assert second.count(["actively_reviewing_applicants"]) == 10
    assert second.count(["be_an_early_applicant"]) == 2
    assert second.count(["actively_reviewing_applicants", "be_an_early_applicant"]) == 1
    assert sum(1 for h in second if h) == 13


def test_a_card_drawing_no_chip_omits_the_key_and_never_says_not_hiring():
    rows = read("c_srch_1")["rows"]
    assert sum(1 for row in rows if "hiring" not in row) == 20


def test_a_chip_word_outside_the_closed_table_is_never_read():
    markup = words("c_srch_1")
    before = sum(1 for r in route.read_ai_search(markup)["rows"] if r.get("hiring"))
    planted = plant(markup, "\nActively reviewing applicants\n", "\nActively reviewing\n", count=5)
    after = sum(1 for r in route.read_ai_search(planted)["rows"] if r.get("hiring"))
    assert (before, after) == (5, 0)


def test_a_chip_word_in_the_head_stack_is_a_title_and_never_a_chip():
    """Only text OUTSIDE the title/employer/place stack is a chip: a title that
    happens to read like one is still a title."""
    markup = words("c_srch_1")
    chipless = next(r["job_id"] for r in route.read_ai_search(markup)["rows"] if "hiring" not in r)
    start = markup.index(f'componentkey="job-card-component-ref-{chipless}"')
    title_slot = 'aria-hidden="true">\nx\n'
    at = markup.index(title_slot, markup.index('data-display-contents="true"', start))
    planted = (markup[:at] + 'aria-hidden="true">\nActively reviewing applicants\n'
               + markup[at + len(title_slot):])
    row = next(r for r in route.read_ai_search(planted)["rows"] if r["job_id"] == chipless)
    assert row["title"] == "Actively reviewing applicants", "the plant must land in the title slot"
    assert "hiring" not in row


def test_proximity_is_read_off_session_12s_cards_a_connection_among_them():
    def readings(stem):
        return [
            (shape.relation_for(r["proximity"]["relation"]), r["proximity"]["count"])
            for r in read(stem)["rows"] if "proximity" in r
        ]

    assert readings("c_srch_1") == [("school_alum", 3), ("school_alum", 1), ("school_alum", 3)]
    assert sorted(readings("c_srch_0b")) == [("connection", 1), ("school_alum", 1), ("school_alum", 1)]


# ---------------------------------------------------------------------------
# 3. The tool asks for the AI route's own address
# ---------------------------------------------------------------------------


def test_the_decision_is_keywords_and_nothing_refused():
    assert route.asks_the_ai_route([], keywords=KEYWORDS) is True
    assert route.asks_the_ai_route([], keywords="   ") is False
    assert route.asks_the_ai_route(["location"], keywords=KEYWORDS) is False
    assert route.ai_search_url("  synthetic   role ") == AI_ASKED


def test_the_ai_address_is_admitted_by_the_read_boundary():
    assert readonly.is_read_url(route.ai_search_url(KEYWORDS)) is True


async def test_a_keyword_search_asks_for_the_ai_routes_own_address(drive):
    """RED BEFORE LANE JOBS7: the tool asked for the classic address and read
    the AI page only after LinkedIn redirected it there."""
    page = _MarkupPage(html=words("c_srch_1"))
    navigations = drive(page)
    result = await linkedin_search_jobs(keywords=KEYWORDS, limit=50)
    assert navigations == [AI_ASKED]
    assert result["route"] == route.AI
    assert result["count"] == 25 and result["page_had"] == 25
    assert "asked for at its own address" in result["note"]
    assert "no longer serves" in result["note"]
    assert sum(1 for row in result["results"] if row.get("hiring")) == 5


async def test_easy_apply_is_applied_to_the_cards_and_never_sent(drive):
    page = _MarkupPage(html=words("c_srch_0b"))
    navigations = drive(page)
    result = await linkedin_search_jobs(keywords=KEYWORDS, easy_apply=True, limit=50)
    assert navigations == [AI_ASKED]
    assert "f_AL" not in navigations[0]
    assert result["easy_apply_post_filter"]["before"] == 18
    assert result["easy_apply_post_filter"]["after"] == 14
    assert all(row["easy_apply"] is True for row in result["results"])


async def test_a_refused_argument_keeps_its_classic_composition_and_refuses_by_name(drive):
    page = _MarkupPage(html=words("c_srch_1"))
    page.redirect_to = AI_ASKED
    navigations = drive(page)
    result = await linkedin_search_jobs(keywords=KEYWORDS, job_type="full_time")
    assert len(navigations) == 1 and navigations[0].startswith(CLASSIC_PREFIX)
    assert "f_JT=F" in navigations[0]
    assert result["error"] == "extraction_failed"
    assert "Refused: job_type" in result["message"]


async def test_a_classic_page_served_at_the_ai_address_is_still_read_as_classic(drive):
    """The reopener's path: should LinkedIn serve the classic page again, the
    classic reader reads it, and the route says which page was read."""
    page = FakePageWithCards()
    page.redirect_to = "https://www.linkedin.com/jobs/search/?keywords=synthetic+role"
    navigations = drive(page)
    result = await linkedin_search_jobs(keywords=KEYWORDS)
    assert navigations == [AI_ASKED]
    assert result["route"] == route.CLASSIC
    assert result["results"][0]["job_id"] == "4111222333"


class FakePageWithCards(_MarkupPage):
    def __init__(self):
        super().__init__(html=None, evaluate_result=[SEARCH_CARD])
