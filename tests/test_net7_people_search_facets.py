"""Four more people-search facets, each spelled as LinkedIn writes it and each a section today's All-filters panel draws (lane net7, 2026-11-27).

THE ROWS (``_audit/_census/network.md``): ``N 86`` Filter by Followers of,
``N 88`` Filter by School, ``N 89`` Filter by Industry, ``N 82`` Filter by
Actively hiring, and ``N 26b`` Filter your connections by school or industry --
the last the same two facets beside ``network="F"``, as ``N 26``'s location and
company halves ride the degree filter.

THE EVIDENCE, TWO HALVES, BOTH CAPTURED:

* THE SECTION IS DRAWN TODAY. Live session 12 opened the people search's All
  filters panel twice (loads 6 and 32). Its keyed skeletons, with LinkedIn's
  words put back where the keyed shape proves them
  (``scripts/_build_live12_net7_word_skeletons.py``), draw an ``h2`` reading
  ``Actively hiring``, ``Followers of``, ``Schools`` and ``Industries`` --
  ``tests/fixtures/synthetic/live12_people_panel_words.html`` and
  ``live12_first_degree_panel_words.html``.
* THE SPELLING IS LINKEDIN'S. ``followerOf`` on session 12's own result cards
  (``tests/fixtures/live12/search_people_labels.html``: a link of ``origin`` and
  ``followerOf``, the value one member token in a percent-encoded JSON list, 51
  characters, ``connectionOf``'s length on the same page); ``schoolFilter``,
  ``industry`` and ``activelyHiring`` on the raw captures lane S read by key
  name and value shape (``_audit/2026-09-24-lane-s-people-search.md``,
  section 2; re-read by lane net7, its record section 2.5). Where LinkedIn is on
  record writing only a BARE value, the JSON list sent is DERIVED, as
  ``pastCompany``'s and ``geoUrn``'s were before their live fires kept them
  verbatim.

``origin`` is never sent. EVERY VALUE IS SYNTHETIC: the member tokens are the
identity guard's declared ``SYNTHETIC_MEMBER_TOKENS``; the ids are digits naming
nothing anybody chose.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
from urllib.parse import parse_qsl, unquote, urlsplit

import pytest

from linkedin_server import people_search, readonly
from tests.test_people_search_readers import _drive, _RecordingBrowser

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE12 = ROOT / "tests" / "fixtures" / "live12"
SYNTHETIC = ROOT / "tests" / "fixtures" / "synthetic"
PANEL = SYNTHETIC / "live12_people_panel_words.html"
FIRST_DEGREE_PANEL = SYNTHETIC / "live12_first_degree_panel_words.html"
SERVER = ROOT / "linkedin_server" / "server.py"

#: Declared synthetic member tokens (``SYNTHETIC_MEMBER_TOKENS``), 39 characters.
TOKEN_A = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000001"
TOKEN_B = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"

#: The followerOf value's length on session 12's result cards, measured by
#: keyed shape (lane net7's record, section 2.5): 51, the same as every
#: connectionOf value on the first-degree page -- a one-token encoded list.
CAPTURED_MEMBER_LIST_CHARACTERS = 51

_HREF = re.compile(r'href="(https://www\.linkedin\.com/search/results/people/\?[^"]*)"')


def _capture_links(capture: pathlib.Path) -> list[list[str]]:
    """The KEY sequence of every people-search link a capture draws."""
    text = capture.read_text(encoding="utf-8")
    return [
        [key for key, _value in parse_qsl(urlsplit(html.unescape(href)).query,
                                          keep_blank_values=True)]
        for href in _HREF.findall(text)
    ]


def _raw_query(url: str) -> list[tuple[str, str]]:
    query = urlsplit(url).query
    return [tuple(pair.split("=", 1)) for pair in query.split("&")] if query else []


def _composed(**kwargs) -> str:
    verdict = people_search.compose(**kwargs)
    assert verdict["built"], verdict
    return verdict["url"]


def _refused(**kwargs) -> dict:
    verdict = people_search.compose(**kwargs)
    assert verdict["built"] is False, verdict
    return verdict


def _panel_headings(path: pathlib.Path) -> list[str]:
    """Every ``h2`` text inside the open panel's ``aside``, in order."""
    text = path.read_text(encoding="ascii")
    aside = text[text.index('aria-hidden="false" tabindex="-1">'):]
    return re.findall(r"<h2[^>]*>\n([^<\n]+)\n</h2>", aside)


# ---------------------------------------------------------------------------
# 1. The captures draw what the facets rest on
# ---------------------------------------------------------------------------


def test_session_12s_result_cards_write_followerOf_beside_origin() -> None:
    """``N 86``'s spelling: LinkedIn's own result-card links, on both searches."""
    assert _capture_links(LIVE12 / "search_people_labels.html").count(["origin", "followerOf"]) == 2
    assert _capture_links(LIVE12 / "search_people_first_degree.html").count(["origin", "followerOf"]) == 3


@pytest.mark.parametrize("path", [PANEL, FIRST_DEGREE_PANEL], ids=["keyword", "first_degree"])
def test_the_open_panel_draws_the_four_sections_by_their_headings(path) -> None:
    headings = _panel_headings(path)
    for section in ("Actively hiring", "Followers of", "Schools", "Industries"):
        assert headings.count(section) == 1, (section, headings)
    # The whole measured form, in the panel's order: two h2s stay x (the
    # panel's own title and the language section's heading).
    assert [h for h in headings if h != "x"] == [
        "Actively hiring", "Connections", "Locations", "Current companies",
        "Connections of", "Followers of", "Past companies", "Schools",
        "Industries", "Service categories",
    ]


def test_the_first_degree_panel_draws_his_first_degree_checked() -> None:
    """``N 26b``'s page: the panel of the search filtered to his first degree."""
    text = FIRST_DEGREE_PANEL.read_text(encoding="ascii")
    assert re.search(r'aria-label="1st" type="checkbox" checked="">', text)


def test_the_open_panel_draws_no_keyword_field() -> None:
    """``N 93``'s reading, held here and NOT a move (lane net7's record,
    section 4): every input inside the open panel is a checkbox or a switch."""
    for path in (PANEL, FIRST_DEGREE_PANEL):
        text = path.read_text(encoding="ascii")
        aside = text[text.index('aria-hidden="false" tabindex="-1">'):text.index("</aside>", text.index('aria-hidden="false" tabindex="-1">'))]
        inputs = re.findall(r"<input [^>]*>", aside)
        assert inputs, path.name
        assert all('type="checkbox"' in tag for tag in inputs), [t for t in inputs if 'type="checkbox"' not in t]


# ---------------------------------------------------------------------------
# 2. The composition
# ---------------------------------------------------------------------------


def test_followers_of_writes_followerOf_as_one_member_token_list() -> None:
    url = _composed(followers_of=TOKEN_A)
    pairs = _raw_query(url)
    assert [k for k, _v in pairs] == ["followerOf"]
    assert json.loads(unquote(pairs[0][1])) == [TOKEN_A]
    assert len(pairs[0][1]) == CAPTURED_MEMBER_LIST_CHARACTERS
    assert readonly.is_read_url(url) is True


def test_followers_of_takes_one_member_and_never_a_slug() -> None:
    assert _refused(followers_of=TOKEN_A + "," + TOKEN_B)["refused"] == "too_many_values"
    refusal = _refused(followers_of="some-member-slug")
    assert refusal["refused"] == "not_a_member_token"
    assert "some-member-slug" not in json.dumps(refusal)


def test_school_ids_write_schoolFilter_as_a_json_list() -> None:
    url = _composed(school_ids="12345678")
    assert [k for k, _v in _raw_query(url)] == ["schoolFilter"]
    assert json.loads(unquote(_raw_query(url)[0][1])) == ["12345678"]
    assert readonly.is_read_url(url) is True


def test_school_ids_refuse_a_name_and_take_at_most_five() -> None:
    assert _refused(school_ids="a-school-slug")["argument"] == "school_ids"
    assert _refused(school_ids="1,2,3,4,5,6")["refused"] == "too_many_values"


def test_industry_ids_write_industry_as_a_json_list() -> None:
    url = _composed(industry_ids="4,96")
    assert [k for k, _v in _raw_query(url)] == ["industry"]
    assert json.loads(unquote(_raw_query(url)[0][1])) == ["4", "96"]


def test_industry_ids_take_digits_only() -> None:
    refusal = _refused(industry_ids="Software Development")
    assert (refusal["argument"], refusal["refused"]) == ("industry_ids", "identifier_is_not_numeric")
    assert _refused(industry_ids="1" * 21)["refused"] == "identifier_too_long"
    # Another script's digits are not LinkedIn's: str.isdigit() would pass it.
    assert _refused(industry_ids="٤")["refused"] == "identifier_is_not_numeric"


def test_actively_hiring_writes_the_json_string_linkedin_writes() -> None:
    url = _composed(actively_hiring=True)
    assert _raw_query(url) == [("activelyHiring", "%22true%22")]
    assert people_search.compose(actively_hiring=False)["url"] == people_search.BASE_URL
    assert people_search.compose(actively_hiring=True)["applied"]["actively_hiring"] == 1


def test_actively_hiring_is_a_switch_and_nothing_else() -> None:
    refusal = _refused(actively_hiring="yes")
    assert (refusal["argument"], refusal["refused"]) == ("actively_hiring", "not_a_switch")


@pytest.mark.parametrize(
    "argument, value, key",
    [("school_ids", "12345678", "schoolFilter"), ("industry_ids", "96", "industry")],
)
def test_his_connections_by_school_or_industry_compose(argument, value, key) -> None:
    """``N 26b``: his first degree filtered by a school or an industry, the
    facet beside the degree filter, as ``N 26``'s halves ride it."""
    url = _composed(network="F", **{argument: value})
    assert [k for k, _v in _raw_query(url)] == ["network", key]
    assert readonly.is_read_url(url) is True


def test_no_new_facet_changes_an_old_composition() -> None:
    """The new keys come AFTER the old ones, so every address composed before
    this lane is composed byte for byte the same."""
    assert people_search.compose()["url"] == people_search.BASE_URL
    old = _composed(keywords="engineer", current_company_ids="1", location_ids="2",
                    network="F", connections_of=TOKEN_A)
    assert [k for k, _v in _raw_query(old)] == [
        "keywords", "currentCompany", "geoUrn", "network", "connectionOf",
    ]
    every = _composed(keywords="engineer", network="F", connections_of=TOKEN_A,
                      followers_of=TOKEN_B, school_ids="3", industry_ids="4",
                      actively_hiring=True)
    assert [k for k, _v in _raw_query(every)] == [
        "keywords", "network", "connectionOf", "followerOf", "schoolFilter",
        "industry", "activelyHiring",
    ]


def test_origin_is_never_sent() -> None:
    url = _composed(followers_of=TOKEN_A, school_ids="3", industry_ids="4", actively_hiring=True)
    assert "origin" not in {k for k, _v in _raw_query(url)}


# ---------------------------------------------------------------------------
# 3. What LinkedIn does with each, read off the address it settles on
# ---------------------------------------------------------------------------


def test_a_bare_value_where_a_list_was_sent_reads_same_values() -> None:
    """LinkedIn is on record writing ``industry`` and ``schoolFilter`` BARE: a
    landing that rewrites the list to the bare spelling keeps the value."""
    asked = _composed(industry_ids="96")
    verdict = people_search.landing_verdict(people_search.BASE_URL + "?industry=96", asked)
    assert verdict["query_kept"] == {"industry_ids": "same_values"}


def test_the_switch_written_bare_reads_same_values() -> None:
    asked = _composed(actively_hiring=True)
    verdict = people_search.landing_verdict(people_search.BASE_URL + "?activelyHiring=true", asked)
    assert verdict["query_kept"] == {"actively_hiring": "same_values"}
    verdict = people_search.landing_verdict(people_search.BASE_URL + "?activelyHiring=%22true%22", asked)
    assert verdict["query_kept"] == {"actively_hiring": "verbatim"}


def test_a_dropped_facet_reads_absent_never_filtered() -> None:
    asked = _composed(followers_of=TOKEN_A, school_ids="3")
    verdict = people_search.landing_verdict(people_search.BASE_URL, asked)
    assert verdict["query_kept"] == {"followers_of": "absent", "school_ids": "absent"}


# ---------------------------------------------------------------------------
# 4. The tool
# ---------------------------------------------------------------------------


def test_the_tool_sends_the_four_facets_and_echoes_none(monkeypatch) -> None:
    browser = _RecordingBrowser()
    payload = _drive(monkeypatch, browser, followers_of=TOKEN_A, school_ids="12345678",
                     industry_ids="96", actively_hiring=True, network="F")
    assert payload["ok"] is True, payload
    assert len(browser.gotos) == 1
    keys = [k for k, _v in _raw_query(browser.gotos[0])]
    assert keys == ["network", "followerOf", "schoolFilter", "industry", "activelyHiring"]
    assert payload["query_applied"]["followers_of"] == 1
    assert payload["query_applied"]["actively_hiring"] == 1
    assert set(payload["query_kept"].values()) == {"verbatim"}
    dumped = json.dumps(payload)
    for value in (TOKEN_A, "12345678"):
        assert value not in dumped


def test_the_tool_refuses_a_slug_before_any_session(monkeypatch) -> None:
    browser = _RecordingBrowser()
    payload = _drive(monkeypatch, browser, followers_of="a-member-slug")
    assert payload["ok"] is False and payload["error"] == "bad_argument"
    assert browser.sessions == 0 and browser.gotos == []


# ---------------------------------------------------------------------------
# 5. The census: each row moved on its own cell's bar, and off every GAP table
# ---------------------------------------------------------------------------

NETWORK = ROOT / "_audit" / "_census" / "network.md"
NEXT_STEP = ROOT / "_audit" / "_census" / "next-step.tsv"
READ_ADDRESSES = ROOT / "_audit" / "_census" / "read-addresses.tsv"

#: row -> (the call its cell names, the panel heading its fixture draws).
MOVED = {
    "82": ("actively_hiring=True", "`Actively hiring`"),
    "86": ("followers_of=<one member token>", "`Followers of`"),
    "88": ("school_ids=<organisation ids>", "`Schools`"),
    "89": ("industry_ids=<industry codes>", "`Industries`"),
}


def _cell(row: str) -> tuple[str, str]:
    for line in NETWORK.read_text(encoding="utf-8").splitlines():
        cells = line.split("|")
        if len(cells) > 5 and cells[1].strip() == row:
            return cells[4].strip(), cells[5].strip()
    raise AssertionError(f"no row {row!r}")


@pytest.mark.parametrize("row", sorted(MOVED))
def test_each_row_is_covered_unfired_and_cites_its_evidence(row) -> None:
    state, cell = _cell(row)
    assert state == "COVERED-UNFIRED"
    paragraph = cell[cell.index("**LANE NET7, 2026-11-27"):]
    call, heading = MOVED[row]
    for words in ("NOT FIRED -- COVERED-UNFIRED", call, heading,
                  "tests/fixtures/synthetic/live12_people_panel_words.html",
                  "tests/test_net7_people_search_facets.py",
                  "_audit/2026-11-27-net7.md"):
        assert words in paragraph, (row, words)


def test_the_moved_rows_left_every_gap_table() -> None:
    rows = list(MOVED) + ["26b"]
    nxt = NEXT_STEP.read_text(encoding="utf-8").splitlines()
    adr = READ_ADDRESSES.read_text(encoding="utf-8").splitlines()
    for row in rows:
        assert not any(line.startswith(f"N {row}\t") for line in nxt), row
        assert not any(line.startswith(f"N\t{row}\t") for line in adr), row
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    import census_completion as cc  # noqa: PLC0415
    import triage_read_gap_rows as triage  # noqa: PLC0415

    for row in rows:
        assert f"N {row}" not in triage.TRIAGE, row
        assert f"N {row}" in cc.PINNED_B1_ROWS[cc.NO_RULING], row
