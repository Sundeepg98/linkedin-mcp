"""``learning`` -- census rows ``J 152``, ``J 154`` and ``J 156`` -- LinkedIn Learning read over its REAL captures.

The three readers run over session 12's captures of the Learning home (load
23), his library's in-progress tab (load 25) and his "My Career Journey" page
(load 24), as ``tests/fixtures/live12/learning_words.html``,
``learning_library_words.html`` and ``learning_journey_words.html`` -- the
committed skeletons with LinkedIn's words written where their keyed shapes
matched (``scripts/_build_build28_word_skeletons.py``) -- through
``tests/skeleton_page.py``, with no browser. Every course title, the goal
line and its bold run are ``x`` in the fixtures, as in the tracked copies;
the tests plant SYNTHETIC ones where the captures drew real ones.

Every title and goal in this file is synthetic.
"""
from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import learning, people_data, readonly
from linkedin_server.errors import ExtractionFailedError
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

LIVE12 = Path(__file__).resolve().parent / "fixtures" / "live12"
HOME = (LIVE12 / "learning_words.html").read_text(encoding="ascii")
LIBRARY = (LIVE12 / "learning_library_words.html").read_text(encoding="ascii")
JOURNEY = (LIVE12 / "learning_journey_words.html").read_text(encoding="ascii")

#: The fifteen carousel cards' durations, in page order, as the capture
#: draws them (measured by keyed shape), in seconds.
DURATIONS = [69 * 60, 50 * 60, 47 * 60, 40 * 60, 55 * 60, 244 * 60, 59 * 60, 113 * 60]

#: A marker no fixture draws: it must never leave, in any field.
MARKER = "Exampleperson Markersurname"


def plant_after(markup: str, anchor: str, values: list[str], slot: str = "\nx\n") -> str:
    """Write each value into the first ``slot`` after each ``anchor``, in
    order; ASSERTED: as many anchors as values, each followed by its slot."""
    assert markup.count(anchor) == len(values), (anchor, markup.count(anchor), len(values))
    at = 0
    for value in values:
        at = markup.index(anchor, at)
        found = markup.index(slot, at)
        markup = markup[:found] + slot.replace("x", value) + markup[found + len(slot):]
        at = found + len(value)
    return markup


TITLES = ["Example course %d" % i for i in range(1, 16)]
HERO_TITLE = "Example featured course"


def home(titles=TITLES, hero=HERO_TITLE) -> str:
    markup = plant_after(HOME, 'class="lls-card-headline', titles)
    return plant_after(markup, 'class="hero-item__headline', [hero])


def library(title="Example course in progress") -> str:
    return plant_after(LIBRARY, 'class="lls-card-headline', [title])


def journey(lead="Example lead words", bold="Example goal role") -> str:
    markup = plant_after(JOURNEY, 'class="career-goal__subtext"', [lead])
    return plant_after(markup, 'class="career-goal__subtext"', [bold], slot="<b>\nx\n</b>")


def run(reader, markup: str, url: str):
    page = SkeletonPage(PlantedPage(), parse(markup), url=url)
    result = asyncio.run(reader(page))
    return result, page


def strings_in(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from strings_in(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from strings_in(item)


# ---------------------------------------------------------------------------
# 1. J 152: the courses the home lists
# ---------------------------------------------------------------------------


def test_the_home_returns_the_hero_and_every_carousel_card_in_page_order():
    result, page = run(learning.read_learning_home, home(), learning.HOME_URL)
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["course_count"] == 16 and result["cards_seen"] == 16
    titles = [c["title"]["text"] for c in result["courses"]]
    assert titles == [HERO_TITLE] + TITLES
    hero, first = result["courses"][0], result["courses"][1]
    assert hero["featured"] is True and hero["badge"] == "popular" and hero["type"] is None
    assert first == {
        "title": people_data.OrganisationProse(text="Example course 1",
                                               read_from="learning_course_title").envelope(),
        "type": "course", "duration_seconds": 69 * 60, "badge": None, "featured": False,
    }
    cards = result["courses"][1:]
    assert all(c["type"] == "course" for c in cards)  # fifteen `Course` labels, measured
    assert [c["badge"] for c in cards].count("popular") == 3  # three card badges, measured
    assert len({c["duration_seconds"] for c in cards}) == 15  # fifteen distinct durations
    assert [c["duration_seconds"] for c in cards][:8] == DURATIONS
    assert result["unknown_types"] == 0 and result["unknown_badges"] == 0
    assert result["cards_withheld"] == 0 and result["cards_unlinked"] == 0
    assert result["reads_failed"] == 0


def test_a_title_leaves_only_inside_its_record_sanitised_and_marked():
    planted = [t.replace("Example", "Example" + chr(0x200B)) for t in TITLES]
    result, _ = run(learning.read_learning_home, home(planted), learning.HOME_URL)
    assert [c["title"]["text"] for c in result["courses"][1:]] == TITLES
    for course in result["courses"]:
        assert course["title"][people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
        others = [t for k, v in course.items() if k != "title" for t in strings_in(v)]
        assert all("Example" not in t for t in others)


def test_a_card_whose_title_does_not_read_is_withheld_and_counted():
    titles = list(TITLES)
    titles[4] = " "
    result, _ = run(learning.read_learning_home, home(titles), learning.HOME_URL)
    assert result["course_count"] == 15 and result["cards_withheld"] == 1


def test_a_type_or_badge_nobody_measured_is_counted_never_returned():
    markup = home().replace("\nCourse\n", "\n" + MARKER + "\n", 1)
    markup = markup.replace("\nPopular\n</div>", "\n" + MARKER + "\n</div>", 1)
    result, _ = run(learning.read_learning_home, markup, learning.HOME_URL)
    assert result["unknown_types"] == 1 and result["unknown_badges"] == 1
    assert MARKER not in json.dumps(result)
    assert [c["type"] for c in result["courses"]].count("other") == 1


def test_a_home_with_no_course_read_raises_rather_than_answering_none():
    with pytest.raises(ExtractionFailedError) as raised:
        run(learning.read_learning_home, HOME.replace("data-view-name", "data-x"), learning.HOME_URL)
    assert raised.value.url == learning.HOME_URL


@pytest.mark.parametrize(
    ("line", "seconds"),
    [("1h 9m", 69 * 60), ("3h", 3 * 3600), ("27m", 27 * 60), ("27m 10s", 27 * 60 + 10),
     ("4h 4m", 244 * 60), ("", None), ("x", None), ("1h 61m", None), ("Course", None), (None, None)],
)
def test_the_duration_grammar_is_linkedins_own(line, seconds):
    assert learning.duration_seconds(line) == seconds


# ---------------------------------------------------------------------------
# 2. J 154: his in-progress tab
# ---------------------------------------------------------------------------


def test_the_in_progress_tab_returns_its_one_course():
    result, page = run(learning.read_in_progress, library(), learning.IN_PROGRESS_URL)
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["tab"] == "in_progress" and result["course_count"] == 1
    assert result["courses"] == [{
        "title": people_data.OrganisationProse(text="Example course in progress",
                                               read_from="learning_course_title").envelope(),
        "type": "course", "duration_seconds": 77 * 60, "badge": None,
        "updated": {"kind": "updated", "month": "2022-04"},
    }]
    assert result["reads_failed"] == 0


def test_another_tab_marked_current_is_not_read_as_in_progress():
    """Move the current marker to the Saved tab: nothing is read as in progress."""
    markup = library()
    current = 'aria-current="page" href="/learning/me/my-library/in-progress"'
    assert markup.count(current) == 1
    markup = markup.replace(current, 'href="/learning/me/my-library/in-progress"')
    saved = 'tabindex="0" href="/learning/me/my-library/saved"'
    assert markup.count(saved) == 1
    markup = markup.replace(saved, 'tabindex="0" aria-current="page" href="/learning/me/my-library/saved"')
    with pytest.raises(ExtractionFailedError):
        run(learning.read_in_progress, markup, learning.IN_PROGRESS_URL)


def test_an_in_progress_tab_with_no_course_read_raises():
    with pytest.raises(ExtractionFailedError) as raised:
        run(learning.read_in_progress, library().replace("learning-my-learning-content-card", "x"),
            learning.IN_PROGRESS_URL)
    assert raised.value.url == learning.IN_PROGRESS_URL


@pytest.mark.parametrize(
    ("line", "read"),
    [("Updated Apr 2022", {"kind": "updated", "month": "2022-04"}),
     ("Released Dec 2019", {"kind": "released", "month": "2019-12"}),
     ("Updated April 2022", None), ("x", None), (None, None)],
)
def test_the_update_line_grammar(line, read):
    assert learning.updated_month(line) == read


# ---------------------------------------------------------------------------
# 3. J 156: his career goal
# ---------------------------------------------------------------------------


def test_his_goal_is_read_off_the_career_goal_section():
    result, page = run(learning.read_career_goal, journey(), learning.JOURNEY_URL)
    assert page.unmodelled == [] and page.planted_answers == []
    assert result == {
        "goal_line": "Example lead words Example goal role",
        "goal": "Example goal role",
        "goal_truncated": False,
        "bold_runs": 1,
        "edit_control_drawn": True,
        "reads_failed": 0,
    }


def test_the_goal_is_sanitised_bounded_and_cut_visibly():
    long = "Example " + "word " * 120
    result, _ = run(learning.read_career_goal, journey(lead=long, bold="Example" + chr(0x202E) + " role"),
                    learning.JOURNEY_URL)
    assert result["goal"] == "Example role"
    assert len(result["goal_line"]) <= learning.GOAL_CAP and result["goal_truncated"] is True


def test_a_line_with_no_bold_run_returns_the_line_and_no_goal():
    markup = journey().replace("<b>\nExample goal role\n</b>", "")
    result, _ = run(learning.read_career_goal, markup, learning.JOURNEY_URL)
    assert result["goal"] is None and result["bold_runs"] == 0
    assert result["goal_line"] == "Example lead words"


@pytest.mark.parametrize(
    "broken",
    [
        lambda m: m.replace('aria-label="Career goal"', 'aria-label="x"'),
        lambda m: m.replace("\nGoal\n", "\nx\n"),
        lambda m: m.replace('class="career-goal__subtext"', 'class="x"'),
    ],
    ids=["no section", "no heading", "no line"],
)
def test_a_page_without_the_measured_section_raises(broken):
    with pytest.raises(ExtractionFailedError) as raised:
        run(learning.read_career_goal, broken(journey()), learning.JOURNEY_URL)
    assert raised.value.url == learning.JOURNEY_URL


# ---------------------------------------------------------------------------
# 4. The addresses and the landings
# ---------------------------------------------------------------------------


def test_each_page_is_the_read_boundarys_admitted_address():
    for url in (learning.HOME_URL, learning.IN_PROGRESS_URL, learning.JOURNEY_URL):
        assert readonly.is_read_url(url), url


@pytest.mark.parametrize(
    ("landed", "path", "ok"),
    [
        ("https://www.linkedin.com/learning/", learning.HOME_PATH, True),
        ("https://www.linkedin.com/learning", learning.HOME_PATH, True),
        ("https://www.linkedin.com/learning/me/my-library/in-progress", learning.IN_PROGRESS_PATH, True),
        ("https://www.linkedin.com/learning/me/my-library/saved/", learning.IN_PROGRESS_PATH, False),
        ("https://www.linkedin.com/learning/career-journey/", learning.JOURNEY_PATH, True),
        ("https://www.linkedin.com/feed/", learning.HOME_PATH, False),
        ("http://www.linkedin.com/learning/", learning.HOME_PATH, False),
        (None, learning.HOME_PATH, False),
    ],
)
def test_a_landing_is_kept_only_on_its_pages_own_path(landed, path, ok):
    assert learning.landed_on(landed, path) is ok


# ---------------------------------------------------------------------------
# 5. The three tools: one load each, its landing checked, then the reader
# ---------------------------------------------------------------------------


def _drive(monkeypatch, markup: str, landing: str) -> list[str]:
    from linkedin_server import browser as browser_module

    navigations: list[str] = []
    page = SkeletonPage(PlantedPage(), parse(markup), url=landing)

    @asynccontextmanager
    async def fake_session():
        yield page

    async def fake_goto(target_page, url, **kwargs):
        navigations.append(url)
        return landing

    monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
    return navigations


@pytest.mark.parametrize(
    ("tool", "markup", "url", "landing"),
    [
        ("linkedin_learning_home", home, learning.HOME_URL, "https://www.linkedin.com/learning/"),
        ("linkedin_learning_in_progress", library, learning.IN_PROGRESS_URL,
         "https://www.linkedin.com/learning/me/my-library/in-progress"),
        ("linkedin_learning_career_goal", journey, learning.JOURNEY_URL,
         "https://www.linkedin.com/learning/career-journey/"),
    ],
)
async def test_each_tool_loads_its_one_admitted_address_and_reads_it(monkeypatch, tool, markup, url, landing):
    from linkedin_server import server

    navigations = _drive(monkeypatch, markup(), landing)
    result = await getattr(server, tool)()
    assert navigations == [url]
    assert result["ok"] is True and result["pages_loaded"] == 1, result


@pytest.mark.parametrize(
    ("tool", "markup"),
    [("linkedin_learning_home", home), ("linkedin_learning_in_progress", library),
     ("linkedin_learning_career_goal", journey)],
)
async def test_each_tool_refuses_a_landing_elsewhere_unread(monkeypatch, tool, markup):
    from linkedin_server import server

    _drive(monkeypatch, markup(), "https://www.linkedin.com/feed/")
    result = await getattr(server, tool)()
    assert result["refused"] == "landed_elsewhere" and result["ok"] is False
    assert "Example" not in json.dumps(result)


# ---------------------------------------------------------------------------
# 6. The fixtures: each differs from its tracked capture only by its declared words
# ---------------------------------------------------------------------------


def _builder_spec() -> dict:
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "_build_build28_word_skeletons.py"
    spec = importlib.util.spec_from_file_location("_build_build28_word_skeletons", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SPEC


@pytest.mark.parametrize("stem", ["learning", "learning_library", "learning_journey"])
def test_each_words_fixture_differs_from_its_capture_only_by_its_declared_words(stem):
    import html as html_module
    import re

    capture, declared = _builder_spec()[stem + "_words"]
    assert capture == stem
    fixture = (LIVE12 / (stem + "_words.html")).read_text(encoding="ascii")
    body = fixture[fixture.index("-->\n") + len("-->\n"):].split("\n")
    copy = (LIVE12 / (stem + ".html")).read_text(encoding="ascii").split("\n")[1:]
    assert len(body) == len(copy)
    differing = [(a, b) for a, b in zip(body, copy) if a != b]
    assert differing
    attribute = re.compile(r'([A-Za-z_:][-A-Za-z0-9_:.]*)="([^"]*)"')
    for written, reduced in differing:
        if not written.startswith("<"):
            assert reduced == "x" and html_module.unescape(written) in declared, written[:60]
            continue
        mine, theirs = attribute.findall(written), attribute.findall(reduced)
        assert [n for n, _ in mine] == [n for n, _ in theirs]
        for (name, value), (_n, was) in zip(mine, theirs):
            if value == was:
                continue
            value, was = html_module.unescape(value), html_module.unescape(was)
            if was == "x":
                assert value in declared, name
                continue
            # AN ADDRESS: only whole path segments equal to a declared path
            # word differ; the query is the copy's, unchanged.
            path, _, query = value.partition("?")
            was_path, _, was_query = was.partition("?")
            assert query == was_query, name
            for got, had in zip(path.split("/"), was_path.split("/")):
                assert got == had or (had == "x" and got in declared), name
