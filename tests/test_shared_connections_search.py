"""Shared connections with a member (census ``N 31``) and a member's own
connections (``N 30``) -- the people searches LinkedIn's own topcard links write.

THE CAPTURE. The live lane's session-2 capture of a first-degree profile, kept
as ``tests/fixtures/live2/first_degree_profile.html`` with every query value
replaced by ``x``, draws three links from the topcard into people search:

    link 1       origin, connectionOf, network      the member's connections
    links 2, 3   origin, network, connectionOf      the connections he shares

Lane L5 measured the VALUE shapes off the gitignored skeleton on 2026-09-28,
values never read (``_audit/2026-09-24-lane-l5-messaging.md``, 'The
orchestrator's calls of 2026-09-28 12:32', S.1): on links 2 and 3 both lists
percent-encoded, ``network`` 13 characters of which 3 are letters --
``["F"]``, his first degree; on link 1 ``network`` 9 characters and 2 letters,
written raw -- ``["F","S"]``.

WHAT THIS FILE HOLDS, each with a check shown able to fail:

1. The capture still draws what this build rests on -- a premise check.
2. ``people_search.compose(connections_of=..., network="F")`` writes the
   capture's keys in the capture's order -- ``network`` then
   ``connectionOf``; ``origin`` is never sent -- and ``network``'s value in
   exactly the shape lane L5 measured.
3. The degrees are LinkedIn's two captured letters and nothing else: a third
   degree is refused, not guessed. And ``network`` is never sent without a
   member named in ``connections_of`` -- LinkedIn is on record writing it only
   beside ``connectionOf``.
4. The address is admitted by the shipped read boundary.
5. The tool returns the shared connections as PEOPLE RECORDS, one page, over
   the same captured skeleton and the same reader
   ``tests/test_people_search_names.py`` holds to the six mitigations.
6. A facet LinkedIn drops reads ``absent``, never filtered.
7. The census: ``N 30`` and ``N 31`` COVERED-UNFIRED on this route, and
   ``N 85``'s spelling MEASURED.

EVERY VALUE IS SYNTHETIC: the member tokens are declared
``SYNTHETIC_MEMBER_TOKENS``, and every person the skeleton draws is from the
declared synthetic tables.
"""

from __future__ import annotations

import asyncio
import contextlib
import html
import pathlib
import re
import sys
from typing import Any
from urllib.parse import parse_qsl, unquote, urlsplit

import pytest

from linkedin_server import people_data, people_search, readonly, search_results
from tests.leakwalk import walk
from tests.test_people_search_names import MUTUALS, PLACE, RESULTS, _drive_tool

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAPTURE = ROOT / "tests" / "fixtures" / "live2" / "first_degree_profile.html"
NETWORK = ROOT / "_audit" / "_census" / "network.md"
SERVER = ROOT / "linkedin_server" / "server.py"

sys.path.insert(0, str(ROOT / "scripts"))

import check_read_addresses as cra  # noqa: E402
import triage_read_gap_rows as triage  # noqa: E402

#: Declared synthetic member tokens (``SYNTHETIC_MEMBER_TOKENS``).
TOKEN_A = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000001"
TOKEN_B = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"

#: THE SHAPES LANE L5 MEASURED on links 2 and 3, values never read: the
#: network list percent-encoded, 13 characters, 3 of them letters.
SHARED_NETWORK_CHARACTERS = 13
SHARED_NETWORK_LETTERS = 3

_HREF = re.compile(r'href="(https://www\.linkedin\.com/search/results/people/\?[^"]*)"')


@pytest.fixture(autouse=True)
def _short_panel_wait(monkeypatch):
    """The filter panel wait polls a page that draws no panel; shortened, as
    ``tests/test_people_search_names.py`` shortens it. The polls are untouched."""
    monkeypatch.setattr(search_results, "PANEL_POLL_MS", 1)


def _capture_links() -> list[list[str]]:
    """The KEY sequence of every people-search link the capture draws."""
    text = CAPTURE.read_text(encoding="utf-8")
    return [
        [key for key, _value in parse_qsl(urlsplit(html.unescape(href)).query,
                                          keep_blank_values=True)]
        for href in _HREF.findall(text)
    ]


def _raw_query(url: str) -> list[tuple[str, str]]:
    """The query pairs as the address WRITES them, percent-encoding kept."""
    query = urlsplit(url).query
    return [tuple(pair.split("=", 1)) for pair in query.split("&")] if query else []


def _composed(**kwargs: Any) -> str:
    verdict = people_search.compose(**kwargs)
    assert verdict["built"], verdict
    return verdict["url"]


def _order_of(link_keys: list[str], url: str) -> bool:
    """Does ``url`` write the capture link's keys, in its order, less origin?"""
    return [key for key, _value in _raw_query(url)] == [
        key for key in link_keys if key != "origin"
    ]


# ---------------------------------------------------------------------------
# 1. The capture still draws what this build rests on
# ---------------------------------------------------------------------------

SHARED_LINK = ["origin", "network", "connectionOf"]
CONNECTIONS_LINK = ["origin", "connectionOf", "network"]


def test_the_capture_draws_the_three_topcard_links_this_build_rests_on() -> None:
    links = _capture_links()
    assert links.count(SHARED_LINK) == 2, links
    assert links.count(CONNECTIONS_LINK) == 1, links
    assert len(links) == 3, links


# ---------------------------------------------------------------------------
# 2. The capture's keys, in its order, and the value in its shape
# ---------------------------------------------------------------------------


def test_the_shared_connections_search_writes_the_captures_keys_in_its_order() -> None:
    url = _composed(connections_of=TOKEN_A, network="F")
    assert _order_of(SHARED_LINK, url), _raw_query(url)
    assert "origin" not in {key for key, _value in _raw_query(url)}


def test_THIS_CONTROL_CAN_FAIL_the_order_check_convicts_the_other_order() -> None:
    """Link 1's order is not links 2 and 3's: the check tells them apart."""
    url = _composed(connections_of=TOKEN_A, network="F")
    assert not _order_of(CONNECTIONS_LINK, url)


def test_the_network_value_is_the_shape_lane_l5_measured_on_the_shared_links() -> None:
    written = dict(_raw_query(_composed(connections_of=TOKEN_A, network="F")))
    value = written["network"]
    assert len(value) == SHARED_NETWORK_CHARACTERS, value
    assert sum(ch.isalpha() for ch in value) == SHARED_NETWORK_LETTERS, value
    assert unquote(value) == '["F"]'
    # And connectionOf is the same grammar, percent-encoded, as on those links.
    member = written["connectionOf"]
    assert member.startswith("%5B%22") and member.endswith("%22%5D"), member
    assert unquote(member) == '["' + TOKEN_A + '"]'


def test_THIS_CONTROL_CAN_FAIL_the_raw_spelling_is_not_the_shared_links_shape() -> None:
    """``["F"]`` written raw is 5 characters and 1 letter -- link 1's grammar,
    not links 2 and 3's -- so the shape check above would convict it."""
    raw = '["F"]'
    assert len(raw) != SHARED_NETWORK_CHARACTERS
    assert sum(ch.isalpha() for ch in raw) != SHARED_NETWORK_LETTERS


def test_two_degrees_are_written_in_the_order_link_1_lists_them() -> None:
    for given in ("F,S", "S,F", " S , F "):
        written = dict(parse_qsl(urlsplit(_composed(connections_of=TOKEN_A, network=given)).query))
        assert written["network"] == '["F","S"]', (given, written["network"])


def test_applied_counts_the_degrees_and_carries_no_value() -> None:
    verdict = people_search.compose(connections_of=TOKEN_A, network="F")
    assert verdict["applied"]["network"] == 1
    assert verdict["applied"]["connections_of"] == 1


# ---------------------------------------------------------------------------
# 3. Two captured letters, and never without a named member
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["O", "f", "s", "1st", "F S", "FS", "first", "Zzqdegreeplant"])
def test_a_degree_the_capture_does_not_hold_is_refused_and_described(value: str) -> None:
    verdict = people_search.compose(connections_of=TOKEN_A, network=value)
    assert verdict["built"] is False, verdict
    assert verdict["argument"] == "network"
    assert verdict["refused"] == "not_a_network_degree"
    assert "characters" in verdict["saw"]
    if len(value) >= 5:
        assert not any(value in text for _where, text in walk(verdict)), verdict


def test_a_repeated_degree_is_refused_not_dropped() -> None:
    verdict = people_search.compose(connections_of=TOKEN_A, network="F,F")
    assert verdict["built"] is False
    assert verdict["refused"] == "duplicate_value"


@pytest.mark.parametrize("others", [{}, {"keywords": "engineer"},
                                    {"current_company_ids": "5417062"}])
def test_network_without_a_named_member_is_refused(others: dict) -> None:
    verdict = people_search.compose(network="F", **others)
    assert verdict["built"] is False, verdict
    assert verdict["argument"] == "network"
    assert verdict["refused"] == "network_needs_a_named_member"
    envelope = people_search.refusal_envelope(verdict)
    assert envelope["error"] == "bad_argument" and envelope["pages_loaded"] == 0


def test_THIS_CONTROL_CAN_FAIL_the_same_degree_with_a_member_is_built() -> None:
    """The refusal above is about the missing member, not the letter."""
    assert people_search.compose(network="F", connections_of=TOKEN_A)["built"] is True


class _NoSessionBrowser:
    """A browser that fails the test if the tool opens a session or loads."""

    def __init__(self) -> None:
        self.sessions = 0
        self.gotos: list[str] = []

    def session(self):
        @contextlib.asynccontextmanager
        async def _session():
            self.sessions += 1
            raise AssertionError("a session was opened")
            yield  # pragma: no cover

        return _session()

    async def goto(self, page: Any, url: str) -> str:
        self.gotos.append(url)
        raise AssertionError("a page was loaded")


def test_the_tool_refuses_network_alone_before_any_session(monkeypatch) -> None:
    from linkedin_server import server

    browser = _NoSessionBrowser()
    monkeypatch.setattr(server, "BROWSER", browser)
    payload = asyncio.run(server.linkedin_people_search_shape(network="F"))
    assert browser.sessions == 0 and browser.gotos == []
    assert payload["ok"] is False
    assert payload["error"] == "bad_argument"
    assert payload["argument"] == "network"
    assert payload["refused"] == "network_needs_a_named_member"
    assert payload["pages_loaded"] == 0


# ---------------------------------------------------------------------------
# 4. Admitted by the shipped read boundary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("degrees", ["F", "S", "F,S"])
def test_the_shared_address_is_admitted_by_the_shipped_boundary(degrees: str) -> None:
    url = _composed(connections_of=TOKEN_B, network=degrees, keywords="engineer")
    assert readonly.is_read_url(url) is True, url
    assert people_search.boundary_verdict(url) == {"admitted": True}
    assert cra.refusal_of(url) == "-"


# ---------------------------------------------------------------------------
# 5. The shared connections come back as people records
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def shared_drive() -> dict[str, Any]:
    return _drive_tool(connections_of=TOKEN_A, network="F", include_names=True)


def test_the_tool_returns_the_shared_connections_as_people_records(shared_drive) -> None:
    assert shared_drive["ok"] is True, shared_drive
    people = shared_drive["people"]
    assert [person["name"] for person in people] == [name for name, _slug, _head in RESULTS]
    for person in people:
        assert set(person) == people_data.PERSON_SHAPE, person
        assert person[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE


def test_the_tool_applies_the_facet_and_loads_one_page(shared_drive) -> None:
    assert shared_drive["query_applied"]["network"] == 1
    assert shared_drive["query_applied"]["connections_of"] == 1
    assert shared_drive["query_kept"]["network"] == "verbatim"
    assert shared_drive["query_kept"]["connections_of"] == "verbatim"
    assert shared_drive["_gotos"] == 1
    assert shared_drive["pages_loaded"] == 1


def test_nothing_about_anybody_crosses_outside_the_records(shared_drive) -> None:
    """The mutual connections the results name, and the location line, cross
    nowhere -- the six mitigations' reader, reached with the facet."""
    outside = {key: value for key, value in shared_drive.items() if key != "people"}
    texts = [text for _where, text in walk(outside)]
    for needle in (*MUTUALS, PLACE, TOKEN_A):
        assert not any(needle in text for text in texts), needle
    for needle in (*MUTUALS, PLACE):
        assert not any(needle in text for _where, text in walk(shared_drive["people"])), needle


# ---------------------------------------------------------------------------
# 6. A facet LinkedIn drops reads absent
# ---------------------------------------------------------------------------


def test_a_dropped_network_facet_reads_absent_not_filtered() -> None:
    asked = _composed(connections_of=TOKEN_A, network="F")
    landed = search_results.PEOPLE_SEARCH_URL + "?connectionOf=%5B%22" + TOKEN_A + "%22%5D"
    kept = people_search.landing_verdict(landed, asked)["query_kept"]
    assert kept == {"network": "absent", "connections_of": "verbatim"}


def test_a_raw_spelling_of_the_same_degrees_reads_same_values() -> None:
    """Link 1's raw spelling of the same list is the same values."""
    asked = _composed(connections_of=TOKEN_A, network="F,S")
    landed = (search_results.PEOPLE_SEARCH_URL + '?network=["S","F"]&connectionOf=%5B%22'
              + TOKEN_A + "%22%5D")
    kept = people_search.landing_verdict(landed, asked)["query_kept"]
    assert kept["network"] == "same_values"


# ---------------------------------------------------------------------------
# 7. The census
# ---------------------------------------------------------------------------

_ROW = re.compile(r"^\|\s*(\d+)\s*\|[^|]*\|\s*R\s*\|\s*\*{0,2}([A-Z-]+)\*{0,2}\s*\|(.*)$")


def _network_rows() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for line in NETWORK.read_text(encoding="utf-8").splitlines():
        found = _ROW.match(line)
        if found:
            out.setdefault(found.group(1), (found.group(2), found.group(3)))
    return out


def test_n30_is_covered_unfired_by_d6_and_its_fire_needs_a_member_he_names() -> None:
    state, cell = _network_rows()["30"]
    assert state == "COVERED-UNFIRED"
    opening = cell.lstrip()
    assert opening.startswith("**COVERED-UNFIRED 2026-09-28 (lane S)"), opening[:120]
    head = opening[: opening.find("**RETURNED TO GAP") if "**RETURNED TO GAP" in opening else None]
    for words in ("D6-CAPABILITY-OVER-AFFORDANCE", "`linkedin_people_search_shape(",
                  "connections_of=", "include_names=True", "A MEMBER HE NAMES",
                  "INCIDENTAL-CAPTURE-IS-NOT-A-RULING",
                  "`tests/test_shared_connections_search.py`"):
        assert words in head, words


def test_n31_is_covered_unfired_on_the_network_facet() -> None:
    state, cell = _network_rows()["31"]
    assert state == "COVERED-UNFIRED"
    opening = cell.lstrip()
    assert opening.startswith("**COVERED-UNFIRED 2026-09-28 (lane S)"), opening[:120]
    for words in ('network="F"', "connections_of=", "include_names=True",
                  "`PEOPLE-DATA-MITIGATIONS`", "A MEMBER HE NAMES",
                  "`tests/test_shared_connections_search.py`"):
        assert words in opening, words


def test_n85_reads_the_spelling_measured_and_cites_the_capture() -> None:
    _state, cell = _network_rows()["85"]
    assert "**THE SPELLING IS MEASURED, 2026-09-28" in cell
    assert "`tests/fixtures/live2/first_degree_profile.html`" in cell
    assert "**THE SPELLING IS DERIVED, AND SAID SO:**" not in cell


def test_the_composers_own_table_reads_connectionof_measured() -> None:
    doc = people_search.__doc__ or ""
    row = next(line for line in doc.splitlines() if line.strip().startswith("connectionOf"))
    assert row.rstrip().endswith("MEASURED"), row
    network = next(line for line in doc.splitlines() if line.strip().startswith("network "))
    assert network.rstrip().endswith("MEASURED"), network


def test_neither_row_is_in_the_address_table_or_the_read_triage() -> None:
    rows, problems = cra.load()
    assert not problems, problems
    by_row = {(r["slice"], r["row"]) for r in rows}
    for row in ("30", "31"):
        assert ("N", row) not in by_row, f"N {row} left bucket 3 and still has a line"
        assert f"N {row}" not in triage.TRIAGE, f"N {row} left the read-gap set"
