"""An organisation Page's About and Events tabs, read over REAL captured markup.

Census rows ``J 106`` (the About tab: size, industry, locations) and ``J 165``
(the Events tab: the events a company hosts). Every reading here runs
``company_tabs.read_about`` or ``read_events`` over session 11's captures of
the two tabs, ``tests/fixtures/live11/company_about_words.html`` and
``company_events_words.html`` -- the committed skeletons with LinkedIn's words
written where their keyed shapes matched -- through ``tests/skeleton_page.py``,
which answers Playwright's locators from the parsed document with no browser.

The Page's own values and every event's words are ``x`` in the fixtures, as
in the captures' tracked copies; each test PLANTS synthetic values into the
markup LinkedIn drew, at the place the capture drew the real one.

Every name-shaped string in this file is synthetic.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import company_tabs as ct
from linkedin_server import people_data
from linkedin_server.errors import ExtractionFailedError
from tests.live11_words import plain, plant, words
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

ABOUT_URL = "https://www.linkedin.com/company/example-org/about/"
EVENTS_URL = "https://www.linkedin.com/company/example-org/events/"

#: A marker no fixture draws: where it is planted, it may come back only
#: inside a record's declared field, or not at all.
MARKER = "Exampleperson Markersurname"


def run(reader, markup: str, url: str) -> tuple[dict[str, Any], SkeletonPage]:
    page = SkeletonPage(PlantedPage(), parse(markup), url=url)
    return asyncio.run(reader(page)), page


def strings_in(value: Any, path: tuple = ()):
    """Every string in ``value`` with the path that holds it, keys included."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield path + ("<key>",), str(key)
            yield from strings_in(item, path + (key,))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from strings_in(item, path + (index,))


def outside_records(value: Any) -> list[str]:
    """Strings that sit outside any people_data record's declared text field."""
    found: list[str] = []

    def walk(item: Any) -> None:
        record = people_data.as_record(item) if isinstance(item, dict) else None
        if record is not None:
            return
        if isinstance(item, str):
            found.append(item)
        elif isinstance(item, dict):
            for key, inner in item.items():
                found.append(str(key))
                walk(inner)
        elif isinstance(item, (list, tuple)):
            for inner in item:
                walk(inner)

    walk(value)
    return found


# ---------------------------------------------------------------------------
# The About tab
# ---------------------------------------------------------------------------

_OVERVIEW_P = '<p class="break-words white-space-pre-wrap t-black--light text-body-medium">\nx\n</p>'
_WEBSITE = '<span class="link-without-visited-state" dir="ltr">\nx\n</span>'


def _dd_after(term: str) -> str:
    return (f"{term}\n</h3>\n</dt>\n<dd class=\"mb4 t-black--light text-body-medium\">\nx\n</dd>")


def about(**values: str) -> str:
    """The About fixture with synthetic values planted where the capture drew
    the Page's own."""
    markup = words("company_about")
    markup = plant(markup, _OVERVIEW_P, _OVERVIEW_P.replace("\nx\n", "\n" + values.get(
        "description", "Example Org makes example things for example people.") + "\n"))
    markup = plant(markup, _WEBSITE, _WEBSITE.replace("\nx\n", "\n" + values.get("website", "example.org") + "\n"))
    for term, default in (("Industry", "Example Industry"), ("Headquarters", "Example City, Example Region")):
        markup = plant(markup, _dd_after(term), _dd_after(term).replace("\nx\n", "\n" + values.get(term, default) + "\n"))
    specialties_old = ("Specialties\n</h3>\n</dt>\n<dd class=\"mb4 t-black--light text-body-medium\" dir=\"ltr\">\nx\n</dd>")
    markup = plant(markup, specialties_old, specialties_old.replace(
        "\nx\n", "\n" + values.get("Specialties", "Example one, example two") + "\n"))
    verified_old = ("</span>\n</dt>\n<dd class=\"mb4 t-black--light text-body-medium\">\nx\n</dd>")
    markup = plant(markup, verified_old, verified_old.replace("\nx\n", "\n" + values.get("verified", "August 21, 2024") + "\n"))
    members_old = "<span>\nx\n</span>\n</a>\n<span tabindex=\"-1\""
    markup = plant(markup, members_old, members_old.replace(
        "\nx\n", "\n" + values.get("members", "123,456 associated members") + "\n"))
    return markup


def test_the_about_tab_returns_its_measured_facts():
    result, page = run(ct.read_about_tab, about(), ABOUT_URL)
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["view"] == "about"
    assert result["overview_headings"] == 1 and result["paragraphs_in_card"] == 1
    assert result["description"] == {
        "text": "Example Org makes example things for example people.",
        "truncated": False,
        "read_from": "about_overview",
        people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
    }
    facts = result["facts"]
    assert set(facts) == {"website", "industry", "headquarters", "specialties"}
    assert facts["industry"]["text"] == "Example Industry"
    assert facts["industry"]["read_from"] == "about_industry"
    assert facts["website"]["text"] == "example.org"
    assert facts["headquarters"]["text"] == "Example City, Example Region"
    assert facts["specialties"]["text"] == "Example one, example two"
    for record in facts.values():
        assert type(people_data.as_record(record)) is people_data.OrganisationProse
    assert result["company_size"] == "10,001+ employees"
    assert result["associated_members"] == 123456
    assert result["verified_on"] == "2024-08-21"
    assert result["locations"] == 45
    assert result["terms_unrecognised"] == 0 and result["values_withheld"] == 0
    assert result["reads_failed"] == 0


def test_with_its_words_reduced_the_about_capture_is_a_failed_read():
    """THE CONTROL: the words are the anchor. The committed copy draws the same
    markup with every word x, and nothing on it says the Page has no details."""
    with pytest.raises(ExtractionFailedError) as caught:
        run(ct.read_about_tab, plain("company_about"), ABOUT_URL)
    assert "x" not in str(caught.value).split("(")[0].split()


def test_the_description_is_the_cards_own_paragraph_not_the_nested_cards():
    """The details card nests a section with a paragraph of its own; a marker
    planted there never becomes the description."""
    markup = about()
    nested = '<p class="text-body-small-open mb4 t-black">'
    assert markup.count(nested) == 1
    result, _ = run(ct.read_about_tab, markup, ABOUT_URL)
    assert result["description"]["text"].startswith("Example Org makes")


def test_an_unmeasured_term_is_counted_and_its_value_never_read():
    markup = about(Industry=MARKER)
    markup = plant(markup, "<h3 class=\"text-heading-medium\">\nIndustry\n</h3>",
                   "<h3 class=\"text-heading-medium\">\nFounded\n</h3>")
    result, _ = run(ct.read_about_tab, markup, ABOUT_URL)
    assert result["terms_unrecognised"] == 1
    assert "industry" not in result["facts"]
    assert all(MARKER not in text for _path, text in strings_in(result))


def test_a_size_outside_linkedins_bands_is_withheld_not_quoted():
    markup = plant(about(), "\n10,001+ employees\n", "\nAbout ten thousand people\n")
    result, _ = run(ct.read_about_tab, markup, ABOUT_URL)
    assert result["company_size"] is None
    assert result["values_withheld"] == 1
    assert all("ten thousand" not in text for _path, text in strings_in(result))


def test_a_date_that_is_not_a_long_date_is_withheld():
    result, _ = run(ct.read_about_tab, about(verified="last week"), ABOUT_URL)
    assert result["verified_on"] is None and result["values_withheld"] == 1


def test_a_planted_name_leaves_only_inside_records():
    result, _ = run(ct.read_about_tab, about(description="Founded by " + MARKER + ".",
                                         Headquarters=MARKER), ABOUT_URL)
    assert any(MARKER in text for _path, text in strings_in(result))
    assert all(MARKER not in text for text in outside_records(result))


def test_two_overview_headings_read_no_card_and_the_zero_raises():
    markup = plant(about(), '<h2 class="t-black link-without-visited-state text-body-small-bold">\nx\n</h2>',
                   '<h2 class="t-black link-without-visited-state text-body-small-bold">\nOverview\n</h2>')
    with pytest.raises(ExtractionFailedError):
        run(ct.read_about_tab, markup, ABOUT_URL)


# ---------------------------------------------------------------------------
# The Events tab
# ---------------------------------------------------------------------------

_EVENT_TEXT = (
    "            t-black\">\nx\n</span>\n"
    "<span class=\"events-components-shared-event-card__event-title t-black\n"
    "            text-body-medium-bold\">\nx\n</span>"
)
_UPCOMING_P = '<p class="t-black--light ml1">\nx\n</p>'

#: Six synthetic events, in the order the capture draws six.
EVENTS = [
    ("Tue, Nov 11, 2025, 3:30 PM", "Example event one", "1111111111111111111"),
    ("Tue, Jun 3, 2025, 10:00 PM", "Example event two", "2222222222222222222"),
    ("Mon, Oct 20, 2025, 9:15 PM", "Example event three", "3333333333333333333"),
    ("Mon, Sep 15, 2025, 8:00 PM", "Example event four", "4444444444444444444"),
    ("Tue, Apr 22, 2025, 7:45 AM", "Example event five", "5555555555555555555"),
    ("Thu, Mar 13, 2025, 12:05 PM", "Example event six", "6666666666666666666"),
]


def events_markup(events=EVENTS, upcoming: str = "Example Org has no upcoming events planned") -> str:
    markup = words("company_events")
    body_start = markup.index("\n-->\n")
    head, body = markup[:body_start], markup[body_start:]
    assert body.count(_EVENT_TEXT) == len(events) and body.count('href="/events/x/"') == len(events)
    for start, title, digits in events:
        body = body.replace('href="/events/x/"', f'href="/events/example-{digits}/"', 1)
        body = body.replace(_EVENT_TEXT, _EVENT_TEXT.replace("\nx\n", "\n" + start + "\n", 1)
                            .replace("\nx\n", "\n" + title + "\n", 1), 1)
    if upcoming is not None:
        assert body.count(_UPCOMING_P) == 1
        body = body.replace(_UPCOMING_P, _UPCOMING_P.replace("\nx\n", "\n" + upcoming + "\n"))
    return head + body


def test_the_events_tab_returns_each_past_event_as_a_record():
    result, page = run(ct.read_events_tab, events_markup(), EVENTS_URL)
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["events_headings"] == 1
    assert set(result["cards"]) == {"upcoming", "past"}
    past = result["cards"]["past"]
    assert past["anchors_seen"] == 6 and past["beyond_bound"] == 0
    assert [e["event"]["title"] for e in past["events"]] == [t for _s, t, _d in EVENTS]
    assert [e["event"]["link"] for e in past["events"]] == [
        f"https://www.linkedin.com/events/{d}/" for _s, _t, d in EVENTS
    ]
    assert [e["starts"] for e in past["events"]] == [
        "2025-11-11T15:30", "2025-06-03T22:00", "2025-10-20T21:15",
        "2025-09-15T20:00", "2025-04-22T07:45", "2025-03-13T12:05",
    ]
    for item in past["events"]:
        assert type(people_data.as_record(item["event"])) is people_data.Event
    assert result["cards"]["upcoming"] == {
        "events": [], "anchors_seen": 0, "beyond_bound": 0, "none_planned": True,
    }
    assert result["more_offered"] is True
    assert result["events_withheld"] == 0 and result["cards_unrecognised"] == 0


def test_with_its_words_reduced_the_events_capture_is_a_failed_read():
    with pytest.raises(ExtractionFailedError):
        run(ct.read_events_tab, plain("company_events"), EVENTS_URL)


def test_no_event_and_no_sentence_is_a_failed_read_never_none():
    """Every event's start unreadable and the Upcoming card silent: nothing
    corroborates a zero, so it raises."""
    broken = [("sometime", t, d) for _s, t, d in EVENTS]
    with pytest.raises(ExtractionFailedError):
        run(ct.read_events_tab, events_markup(broken, upcoming=None), EVENTS_URL)


def test_the_upcoming_sentence_alone_corroborates_an_empty_tab():
    broken = [("sometime", t, d) for _s, t, d in EVENTS]
    result, _ = run(ct.read_events_tab, events_markup(broken), EVENTS_URL)
    assert result["cards"]["upcoming"]["none_planned"] is True
    assert result["cards"]["past"]["events"] == []
    assert result["events_withheld"] == 6


def test_the_sentence_is_matched_on_linkedins_tail_and_never_returned():
    result, _ = run(ct.read_events_tab, events_markup(upcoming=MARKER + " has no upcoming events planned"), EVENTS_URL)
    assert result["cards"]["upcoming"]["none_planned"] is True
    assert all(MARKER not in text for _path, text in strings_in(result))


def test_an_event_title_leaves_only_inside_its_record():
    planted = [(s, MARKER if i == 2 else t, d) for i, (s, t, d) in enumerate(EVENTS)]
    result, _ = run(ct.read_events_tab, events_markup(planted), EVENTS_URL)
    assert any(MARKER in text for _path, text in strings_in(result))
    assert all(MARKER not in text for text in outside_records(result))


def test_an_unknown_card_heading_is_counted_and_its_events_not_read():
    markup = plant(events_markup(), "\nPast events\n", "\nPast meetups\n")
    with pytest.raises(ExtractionFailedError):
        # The Upcoming card still says none are planned, but the six past
        # events are under a heading this reader does not know.
        result, _ = run(ct.read_events_tab, plant(markup, "has no upcoming events planned", "x"), EVENTS_URL)


# ---------------------------------------------------------------------------
# The address and the landing
# ---------------------------------------------------------------------------


def test_each_tab_is_composed_from_the_numeric_id_and_a_constant():
    assert ct.tab_url("5417062", "about") == {
        "built": True, "url": "https://www.linkedin.com/company/5417062/about/",
        "identifier": "5417062", "tab": "about",
    }
    assert ct.tab_url("5417062", "events")["url"] == "https://www.linkedin.com/company/5417062/events/"


# "life" LEFT 2026-11-26 (lane build-jobs2, census J 109): it is a tab now;
# "jobs" is a tab the Page draws and this does not read.
@pytest.mark.parametrize("tab", ["About", "people", "jobs", "../about", "", None, 3])
def test_any_other_tab_is_refused_without_repeating_it(tab):
    refused = ct.tab_url("5417062", tab)
    assert refused["built"] is False and refused["refused"] == "unknown_tab"
    if isinstance(tab, str) and tab:
        assert tab not in refused["why"].replace("'about'", "").replace("'events'", "")


def test_a_slug_is_refused_as_the_root_composer_refuses_it():
    refused = ct.tab_url("example-org", "about")
    assert refused["built"] is False


@pytest.mark.parametrize("landed,tab,ok", [
    ("https://www.linkedin.com/company/example-org/about/", "about", True),
    ("https://www.linkedin.com/company/5417062/about", "about", True),
    ("https://www.linkedin.com/company/example-org/events/", "events", True),
    ("https://www.linkedin.com/company/example-org/", "about", False),
    ("https://www.linkedin.com/company/unavailable/about/", "about", False),
    ("https://www.linkedin.com/company/example-org/about/", "events", False),
    ("https://example.org/company/example-org/about/", "about", False),
    ("http://www.linkedin.com/company/example-org/about/", "about", False),
    (None, "about", False),
])
def test_the_landing_may_veto(landed, tab, ok):
    assert ct.landed_on_tab(landed, tab) is ok


# ---------------------------------------------------------------------------
# The Insights tab, at insightType=HEADCOUNT
# ---------------------------------------------------------------------------

INSIGHTS_URL = "https://www.linkedin.com/company/example-org/insights/?insightType=HEADCOUNT"

#: The eleven functions the capture's table drew, in its order.
FUNCTIONS = [
    "Engineering", "Information Technology", "Sales", "Program and Project Management",
    "Operations", "Product Management", "Business Development", "Arts and Design",
    "Marketing", "Finance", "Support",
]


def insights_markup(values=None, *, function_override=None) -> str:
    """The Insights fixture with synthetic figures planted into each row of
    the screen-reader table, in the order of its cells: employees, share,
    then each growth cell's two spans."""
    markup = words("company_insights_headcount")
    start = markup.index('<table summary="Total job openings"')
    end = markup.index("</table>", start)
    table = markup[start:end]
    rows = table.split("<tr>")
    assert len(rows) == 1 + 1 + len(FUNCTIONS)
    out = [rows[0], rows[1]]
    for index, row in enumerate(rows[2:]):
        employees, share, g3, g6 = (values or {}).get(index, (str(1000 - 50 * index), str(20 - index), "75", "-35"))
        for value in (employees, share, g3 + "%", g3 + "% increase" if not g3.startswith("-") else g3 + "% decrease",
                      g6 + "%", g6 + "% increase" if not g6.startswith("-") else g6 + "% decrease"):
            assert "\nx\n" in row
            row = row.replace("\nx\n", "\n" + value + "\n", 1)
        if function_override and index in function_override:
            row = row.replace("\n" + FUNCTIONS[index] + "\n", "\n" + function_override[index] + "\n", 1)
        out.append(row)
    return markup[:start] + "<tr>".join(out) + markup[end:]


#: J114-READS-ITS-OWN-TABLE (the orchestrator, 2026-11-27; lane jobs7's
#: record, sections 11.5 and 11.6). Session 11's one function table is
#: summarised ``Total job openings``, so its rows are row ``J 174``'s
#: ``openings_by_function``: each function's job openings. Until that ruling
#: the tests below pinned the same rows as ``functions``, with employee
#: counts. ``J 114``'s ``functions`` come from the table summarised
#: ``Headcount growth by function``, which this capture does not draw
#: (``tests/test_the_insights_tables_are_read_by_their_summary.py`` reads it
#: on session 12's load 20).


def test_the_insights_tab_returns_its_modules_and_each_openings_row():
    result, page = run(ct.read_insights_tab, insights_markup(), INSIGHTS_URL)
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["view"] == "insights"
    assert result["modules"] == ["hiring_trends", "total_job_openings"]
    assert result["functions"] == []
    assert result["functions_unread"] == "no_table_with_this_summary"
    assert result["openings_by_function_unread"] is None and result["headers_unread"] == 0
    assert [row["function"] for row in result["openings_by_function"]] == FUNCTIONS
    first = result["openings_by_function"][0]
    assert first == {
        "function": "Engineering", "openings": 1000, "share_of_openings_percent": 20,
        "growth_3_months_percent": 75, "growth_6_months_percent": -35,
    }
    assert result["rows_withheld"] == 0 and result["reads_failed"] == 0


def test_with_its_words_reduced_the_insights_capture_is_a_failed_read():
    with pytest.raises(ExtractionFailedError):
        run(ct.read_insights_tab, plain("company_insights_headcount"), INSIGHTS_URL)


def test_a_function_outside_linkedins_taxonomy_is_withheld():
    result, _ = run(ct.read_insights_tab, insights_markup(function_override={3: MARKER}), INSIGHTS_URL)
    assert result["rows_withheld"] == 1
    assert len(result["openings_by_function"]) == len(FUNCTIONS) - 1
    assert all(MARKER not in text for _path, text in strings_in(result))


def test_a_growth_whose_sign_disagrees_with_its_word_is_withheld_not_flipped():
    markup = insights_markup()
    start = markup.index('<table summary="Total job openings"')
    planted = markup[:start] + markup[start:].replace("\n75% increase\n", "\n-75% increase\n", 1)
    result, _ = run(ct.read_insights_tab, planted, INSIGHTS_URL)
    assert result["openings_by_function"][0]["growth_3_months_percent"] is None


def test_a_cell_is_read_under_the_header_it_names_not_its_position():
    """Swap two header cells' ids: the cells follow their ids, so the counts
    land under the swapped names -- the wiring is what is read."""
    markup = insights_markup()
    start = markup.index('<table summary="Total job openings"')
    head_end = markup.index("</thead>", start)
    head = markup[start:head_end]
    ids = [line.split('"')[1] for line in head.split("\n") if line.startswith("<th id=")]
    assert len(ids) == 5
    swapped = head.replace(ids[1], "SWAP").replace(ids[2], ids[1]).replace("SWAP", ids[2])
    result, _ = run(ct.read_insights_tab, markup[:start] + swapped + markup[head_end:], INSIGHTS_URL)
    first = result["openings_by_function"][0]
    # The share cell now names the count's header, and the count's cell the
    # share header -- whose bound (at most 100) withholds 1000.
    assert first["openings"] == 20
    assert first["share_of_openings_percent"] is None


def test_the_insights_tab_is_composed_with_its_one_admitted_query():
    assert ct.tab_url("5417062", "insights")["url"] == (
        "https://www.linkedin.com/company/5417062/insights/?insightType=HEADCOUNT"
    )
    assert ct.landed_on_tab(
        "https://www.linkedin.com/company/example-org/insights/?insightType=HEADCOUNT", "insights")


# ---------------------------------------------------------------------------
# The Page's posts (J 168), off the Page root's Posts view (session 9)
# ---------------------------------------------------------------------------

POSTS_VIEW = Path(__file__).resolve().parent / "fixtures" / "live9" / "company_root_posts_view.html"
ROOT_URL = "https://www.linkedin.com/company/example-org/"
_BOX = 'data-testid="expandable-text-box">x'


def posts_markup(words_for=lambda i: "Example Page update %d" % (i + 1)) -> str:
    """Session 9's Posts view with a synthetic first line planted in each of
    its thirteen text boxes, in document order."""
    markup = POSTS_VIEW.read_text(encoding="ascii")
    assert markup.count(_BOX) == 13
    for index in range(13):
        markup = markup.replace(_BOX, 'data-testid="expandable-text-box">' + words_for(index), 1)
    return markup


def test_the_posts_view_returns_each_item_with_one_text_box_as_a_record():
    result, page = run(ct.read_posts_tab, posts_markup(), ROOT_URL)
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["view"] == "posts"
    assert result["items_seen"] == 13
    assert len(result["posts"]) == 11
    assert result["posts_without_text"] == 1
    assert result["posts_with_several_text_boxes"] == 1
    for record in result["posts"]:
        assert record["read_from"] == "page_post"
        assert record["text"].startswith("Example Page update ")
        assert type(people_data.as_record(record)) is people_data.OrganisationProse


def test_a_reshares_two_boxes_are_never_read():
    """MEASURED ON THE CAPTURE: in document order the thirteen boxes belong to
    the feed items one box each, except that the sixth item holds the fifth
    and sixth boxes and the second holds none. Each box is planted with its
    own number; the two of the two-box item never come back."""
    result, _ = run(ct.read_posts_tab, posts_markup(lambda i: "Example box %d" % i), ROOT_URL)
    returned = [int(r["text"].split()[2]) for r in result["posts"]]
    assert returned == [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12]


def test_with_no_feed_item_heading_the_root_is_a_failed_read():
    markup = posts_markup().replace("<span>Feed post</span>", "<span>x</span>")
    with pytest.raises(ExtractionFailedError):
        run(ct.read_posts_tab, markup, ROOT_URL)


def test_two_marked_anchors_to_the_same_tab_are_one_tab_and_different_tabs_disagree():
    result, _ = run(ct.read_posts_tab, posts_markup(), ROOT_URL)
    assert result["view"] == "posts"
    split = posts_markup().replace(
        '<a aria-current="true" href="https://www.linkedin.com/company/x/posts/?feedView=x">',
        '<a aria-current="true" href="https://www.linkedin.com/company/x/about/">', 1)
    result, _ = run(ct.read_posts_tab, split, ROOT_URL)
    assert result["view"] == "tabs_disagree"


def test_the_posts_are_read_off_the_root_address():
    assert ct.tab_url("5417062", "posts")["url"] == "https://www.linkedin.com/company/5417062/"
    assert ct.landed_on_tab(ROOT_URL, "posts")
    assert ct.landed_on_tab(ROOT_URL + "posts/", "posts")
    assert not ct.landed_on_tab(ROOT_URL + "about/", "posts")
