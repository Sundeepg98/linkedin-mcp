"""Lane S: the people search takes a keyword and four facets -- from its ARGUMENTS only.

Census rows ``N 79``, ``N 194`` (a keyword), ``N 84``, ``N 87`` (current and
past company), ``N 94`` (several locations in one search), ``N 85`` and
``N 172`` (a member's connections), under ``D1-SEARCH-AS-READS`` and
``OTHER-MEMBER-IDS-AS-READS``. The composer is ``linkedin_server/people_search.py``;
the tool is ``linkedin_people_search_shape``, extended rather than duplicated.

WHAT THIS FILE PROVES, in the order the brief asked for it:

1. EVERY COMPOSED ADDRESS IS ADMITTED by the SHIPPED read boundary -- over a
   corpus of every argument alone, in combination and at its value ceiling --
   and the check is shown able to say REFUSED on the same run.
2. NOTHING PAGE-DERIVED CAN ENTER AN ADDRESS: the composer takes no page and
   imports no browser (its AST), the tool hands it its own parameters and
   nothing else (the tool's AST), and a driven tool whose page AND landing
   carry plants navigates to the composed address and to no other (a
   recording browser, with a control that shows the recorder convicting a
   second navigation).
3. A KEYWORD THE BOUNDARY REFUSES GETS THE BOUNDARY'S OWN ANSWER, with no
   session opened, and the refusal reading is driven beside the census
   instrument's own reader so the two cannot drift.
4. NOTHING A CALLER PASSES COMES BACK, and a refused value is described by its
   shape, never quoted.

EVERY VALUE HERE IS SYNTHETIC AND ARGUES FOR ITSELF: the organisation ids are
members of ``tests/test_no_committed_identity.SYNTHETIC_IDS``, the member
token is one of its ``SYNTHETIC_MEMBER_TOKENS``, the geo ids are the ``100`` /
``200`` placeholders ``_audit/_census/read-addresses.tsv`` already used for
``N 94``, and every keyword is a generic word or carries ``example``. None
identifies the operator: not his name, employer, campus or city.
"""

from __future__ import annotations

import ast
import asyncio
import contextlib
import itertools
import pathlib
import re
import sys
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

import pytest

from linkedin_server import people_search, readonly, search_results
from tests.leakwalk import url_spellings, walk
from tests.plantedpage import PLANT

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE = ROOT / "linkedin_server" / "people_search.py"
SERVER = ROOT / "linkedin_server" / "server.py"
NETWORK = ROOT / "_audit" / "_census" / "network.md"

sys.path.insert(0, str(ROOT / "scripts"))

import check_read_addresses as cra  # noqa: E402

#: Synthetic organisation ids -- both in ``SYNTHETIC_IDS``.
ORG_A = "5417062"
ORG_B = "53000017"
#: The geo placeholders the address table already used for N 94.
GEO_A = "100"
GEO_B = "200"
#: A declared synthetic member token (``SYNTHETIC_MEMBER_TOKENS``).
TOKEN_A = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000001"
TOKEN_B = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"
#: A keyword distinctive enough that finding it anywhere in a payload means it
#: was echoed, and generic enough to identify nobody.
MARKER_KEYWORD = "examplekeywordmarker"

#: A planted slug for the landing: a slug is a name.
PLANTED_SLUG = "example-markerperson-0a1b2c3d4e"
PLANTS = tuple(sorted(url_spellings(PLANT) | url_spellings(PLANTED_SLUG)))

#: The seven rows this lane built, and the state each was banked at.
ROWS = ("79", "84", "85", "87", "94", "172", "194")


def _query(url: str) -> list[tuple[str, str]]:
    return parse_qsl(urlsplit(url).query, keep_blank_values=True)


def _composed(**kwargs: Any) -> str:
    verdict = people_search.compose(**kwargs)
    assert verdict["built"], verdict
    return verdict["url"]


# ---------------------------------------------------------------------------
# 1. Composition -- LinkedIn's own spellings, from the arguments
# ---------------------------------------------------------------------------


def test_no_argument_composes_exactly_the_address_the_tool_always_opened() -> None:
    """The no-argument call is byte-identical to the shipped one, which is what
    ``N 83``'s COVERED-PROVEN rests on."""
    verdict = people_search.compose()
    assert verdict["built"] is True
    assert verdict["url"] == search_results.PEOPLE_SEARCH_URL
    assert set(verdict["applied"].values()) == {0}


@pytest.mark.parametrize(
    "kwargs, expected_query",
    [
        # N 79. The spelling LinkedIn writes: space as '+'.
        ({"keywords": "senior engineer"}, "keywords=senior+engineer"),
        # N 194, and it is EXACTLY the address the bucket-3 table recorded.
        ({"keywords": "#hiring"}, "keywords=%23hiring"),
        # N 84: LinkedIn's faceted JSON-list spelling, measured on the company
        # root capture.
        ({"current_company_ids": ORG_A}, "currentCompany=%5B%22" + ORG_A + "%22%5D"),
        # N 87: the same grammar (bare on record; the list is DERIVED).
        ({"past_company_ids": ORG_A}, "pastCompany=%5B%22" + ORG_A + "%22%5D"),
        # N 94, EXACTLY the multi-value spelling the bucket-3 table drove.
        (
            {"location_ids": GEO_A + "," + GEO_B},
            "geoUrn=%5B%22100%22%2C%22200%22%5D",
        ),
        # N 85 / N 172.
        ({"connections_of": TOKEN_A}, "connectionOf=%5B%22" + TOKEN_A + "%22%5D"),
    ],
)
def test_each_argument_composes_linkedins_spelling(kwargs, expected_query) -> None:
    url = _composed(**kwargs)
    assert url == search_results.PEOPLE_SEARCH_URL + "?" + expected_query


def test_the_rows_recorded_addresses_are_what_the_composer_builds() -> None:
    """The bucket-3 table's own addresses for N 94 and N 194, rebuilt."""
    assert _composed(keywords="#hiring") == (
        "https://www.linkedin.com/search/results/people/?keywords=%23hiring"
    )
    assert _composed(location_ids="100,200") == (
        "https://www.linkedin.com/search/results/people/"
        "?geoUrn=%5B%22100%22%2C%22200%22%5D"
    )


def test_the_address_order_is_fixed_keywords_first_then_the_facets() -> None:
    url = _composed(
        connections_of=TOKEN_A,
        location_ids=GEO_A,
        past_company_ids=ORG_B,
        current_company_ids=ORG_A,
        keywords="engineer",
    )
    keys = [key for key, _value in _query(url)]
    assert keys == ["keywords", "currentCompany", "pastCompany", "geoUrn", "connectionOf"]


def test_applied_counts_what_each_argument_contributed_and_carries_no_value() -> None:
    verdict = people_search.compose(
        keywords=MARKER_KEYWORD,
        current_company_ids=ORG_A + "," + ORG_B,
        location_ids=GEO_A,
        connections_of=TOKEN_A,
    )
    assert verdict["applied"] == {
        "keywords": 1,
        "current_company_ids": 2,
        "past_company_ids": 0,
        "location_ids": 1,
        "connections_of": 1,
    }
    assert all(isinstance(value, int) for value in verdict["applied"].values())


# ---------------------------------------------------------------------------
# 2. Every composed address is ADMITTED by the shipped boundary
# ---------------------------------------------------------------------------

#: One value set per argument, including each facet at its ceiling.
_ONE = {
    "keywords": ["engineer", "#hiring", "senior engineer", "example-keyword 2"],
    "current_company_ids": [ORG_A, ORG_A + "," + ORG_B, ",".join(["610427", "508933", "902611", ORG_A, ORG_B])],
    "past_company_ids": [ORG_B, ORG_A + " , " + ORG_B],
    "location_ids": [GEO_A, GEO_A + "," + GEO_B, "1,2,3,4,5"],
    "connections_of": [TOKEN_A, TOKEN_B],
}


def _corpus() -> list[dict[str, str]]:
    """Every argument alone, every pair, and all five together."""
    out: list[dict[str, str]] = [{}]
    names = sorted(_ONE)
    for name in names:
        out.extend({name: value} for value in _ONE[name])
    for left, right in itertools.combinations(names, 2):
        out.append({left: _ONE[left][-1], right: _ONE[right][-1]})
    out.append({name: _ONE[name][-1] for name in names})
    return out


def test_the_corpus_is_not_empty() -> None:
    assert len(_corpus()) >= 25


@pytest.mark.parametrize("kwargs", _corpus(), ids=lambda kw: "+".join(sorted(kw)) or "none")
def test_every_composed_address_is_admitted_by_the_shipped_boundary(kwargs) -> None:
    url = _composed(**kwargs)
    assert readonly.is_read_url(url) is True, url
    assert people_search.boundary_verdict(url) == {"admitted": True}
    # And by the census instrument's own reader of the same gate.
    assert cra.refusal_of(url) == "-"


def test_THIS_CONTROL_CAN_FAIL_the_admission_check_can_say_refused() -> None:
    """The corpus test above is not vacuous: the same checks say REFUSED here."""
    url = _composed(keywords="settings")
    assert readonly.is_read_url(url) is False
    assert people_search.boundary_verdict(url)["admitted"] is False
    assert cra.refusal_of(url) == "FORBIDDEN[settings]+PATTERN-WOULD-ADMIT"


# ---------------------------------------------------------------------------
# 3. A keyword the boundary refuses gets the boundary's own answer
# ---------------------------------------------------------------------------

#: The eleven ordinary keywords of
#: ``_audit/2026-09-19-search-admission-preconditions.md`` B.4.
REFUSED_KEYWORDS = (
    "invitation", "password", "verification", "settings",
    "visibility", "cookies", "open-to-work", "two-factor",
)
CLEAN_KEYWORDS = ("recruiter", "engineer", "director")


@pytest.mark.parametrize("keyword", REFUSED_KEYWORDS)
def test_a_keyword_that_trips_a_forbidden_substring_gets_the_boundarys_answer(
    keyword: str,
) -> None:
    verdict = people_search.boundary_verdict(_composed(keywords=keyword))
    assert verdict["admitted"] is False
    assert verdict["boundary_refusal"] == "FORBIDDEN"
    assert verdict["boundary_kind"] == readonly.WriteAttemptError.kind
    substring = verdict["forbidden_substring"]
    assert substring in readonly._FORBIDDEN_URL_SUBSTRINGS
    assert substring in keyword
    # The people pattern admits any query shape, so the substring ALONE refuses.
    assert verdict["a_read_pattern_admits_the_address"] is True
    assert verdict["arguments_carrying_it"] == ["keywords"]
    # Written for a person who was searching, not "not a read surface".
    assert "not a read surface" not in verdict["why"]
    assert "Nothing was loaded" in verdict["why"]


@pytest.mark.parametrize("keyword", CLEAN_KEYWORDS)
def test_the_three_clean_ordinary_keywords_are_admitted(keyword: str) -> None:
    assert people_search.boundary_verdict(_composed(keywords=keyword)) == {"admitted": True}


def test_the_eleven_are_split_eight_and_three_as_b4_measured() -> None:
    refused = [k for k in REFUSED_KEYWORDS + CLEAN_KEYWORDS
               if not readonly.is_read_url(_composed(keywords=k))]
    assert sorted(refused) == sorted(REFUSED_KEYWORDS)


def test_a_refused_keyword_is_not_quoted_back_in_the_envelope() -> None:
    keyword = "exampleperson settings"
    envelope = people_search.refusal_envelope(
        people_search.boundary_verdict(_composed(keywords=keyword))
    )
    assert envelope["error"] == "refused_by_the_read_boundary"
    assert envelope["pages_loaded"] == 0
    texts = [text for _where, text in walk(envelope)]
    assert not any("exampleperson" in text for text in texts), envelope


def test_the_refusal_reading_agrees_with_the_census_instruments_reader() -> None:
    """Two readers of the gate's one sentence, driven over the same refusals.

    ``scripts/check_read_addresses.kind_of_refusal`` is the census instrument;
    ``people_search.boundary_verdict`` is the tool's. If the gate's sentence is
    ever reworded, both must move together or this goes red.
    """
    for keyword in REFUSED_KEYWORDS:
        url = _composed(keywords=keyword)
        verdict = people_search.boundary_verdict(url)
        census = cra.refusal_of(url)
        assert census == (
            f"FORBIDDEN[{verdict['forbidden_substring']}]+PATTERN-WOULD-ADMIT"
        )


def test_the_substring_is_published_only_from_the_boundarys_own_tuple(monkeypatch) -> None:
    """A sentence naming a substring the tuple does not hold publishes nothing."""

    def _lying_gate(url: str) -> str:
        raise readonly.WriteAttemptError(
            f"navigation blocked: {url!r} contains '{MARKER_KEYWORD}', which is "
            "not a read surface. A READ PATTERN DOES ADMIT THIS ADDRESS"
        )

    monkeypatch.setattr(readonly, "assert_read_url", _lying_gate)
    verdict = people_search.boundary_verdict(_composed(keywords="engineer"))
    assert verdict["admitted"] is False
    assert verdict["forbidden_substring"] is None
    assert verdict["boundary_refusal"] == "UNREADABLE"
    assert not any(MARKER_KEYWORD in text for _w, text in walk(verdict))


# ---------------------------------------------------------------------------
# 4. A refused ARGUMENT is described, never quoted
# ---------------------------------------------------------------------------

#: (argument, a value that must be refused, the refusal literal)
BAD_ARGUMENTS = (
    ("current_company_ids", "example-org", "identifier_is_not_numeric"),
    ("past_company_ids", "exampleorgslug", "identifier_is_not_numeric"),
    # Arabic-Indic digits: str.isdigit() is True of them, the ten ASCII are not.
    ("current_company_ids", "\u0661\u0662\u0663\u0664", "identifier_is_not_numeric"),
    ("location_ids", "\u0661\u0662\u0663", "identifier_is_not_numeric"),
    ("location_ids", "example-city", "identifier_is_not_numeric"),
    ("location_ids", "1" * 21, "identifier_too_long"),
    ("current_company_ids", "1" * 21, "identifier_too_long"),
    ("location_ids", "100,,200", "empty_value"),
    ("location_ids", "100,", "empty_value"),
    ("location_ids", "100,100", "duplicate_value"),
    ("location_ids", "1,2,3,4,5,6", "too_many_values"),
    ("current_company_ids", ",".join(str(n) for n in range(1001, 1007)), "too_many_values"),
    # A profile slug is a name, and the ruling permits an id.
    ("connections_of", "example-person-1a2b", "not_a_member_token"),
    ("connections_of", TOKEN_A + "," + TOKEN_B, "too_many_values"),
    ("connections_of", "ACoAAshort", "not_a_member_token"),
    ("keywords", "x" * 201, "keywords_too_long"),
    ("keywords", "example\nkeyword", "keywords_carry_a_control_character"),
)


@pytest.mark.parametrize("argument, value, refused", BAD_ARGUMENTS)
def test_a_refused_argument_names_itself_and_describes_the_value(
    argument: str, value: str, refused: str
) -> None:
    verdict = people_search.compose(**{argument: value})
    assert verdict["built"] is False
    assert verdict["argument"] == argument
    assert verdict["refused"] == refused
    envelope = people_search.refusal_envelope(verdict)
    assert envelope["error"] == "bad_argument"
    assert envelope["pages_loaded"] == 0
    # THE VALUE IS NEVER QUOTED. Every piece of it that could be a name is
    # hunted -- the whole value, and each comma-separated member.
    needles = {value} | {piece for piece in value.split(",") if len(piece) >= 5}
    needles = {n for n in needles if len(n) >= 5 and not n.isdigit()}
    for _where, text in walk(envelope):
        for needle in needles:
            assert needle not in text, (argument, needle, envelope)


@pytest.mark.parametrize(
    "keyword",
    [
        # A no-break space, and a zero-width joiner as several Indian scripts
        # use inside a word. ``str.isprintable()`` is False for both, which is
        # why the composer refuses control characters by CATEGORY instead.
        "example" + chr(0x00A0) + "keyword",
        "example" + chr(0x200D) + "keyword",
    ],
)
def test_a_keyword_in_an_ordinary_script_is_not_mistaken_for_a_control_character(
    keyword: str,
) -> None:
    verdict = people_search.compose(keywords=keyword)
    assert verdict["built"] is True, verdict
    assert readonly.is_read_url(verdict["url"]) is True


def test_a_non_string_argument_never_raises() -> None:
    for value in (None, 0, 12345, ["x"], {"a": 1}):
        verdict = people_search.compose(current_company_ids=value)
        assert isinstance(verdict, dict)


# ---------------------------------------------------------------------------
# 5. Nothing page-derived can enter an address
# ---------------------------------------------------------------------------


def _tree(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def test_the_composer_touches_no_page_and_no_browser() -> None:
    """The structural half of the derivation proof, read off the module's AST."""
    tree = _tree(MODULE)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = [a.arg for a in node.args.args + node.args.kwonlyargs]
            assert "page" not in params, f"{node.name} takes a page"
            assert not isinstance(node, ast.AsyncFunctionDef), (
                f"{node.name} is a coroutine; the composer does no I/O"
            )
        elif isinstance(node, ast.Attribute):
            assert node.attr not in {"goto", "evaluate", "content", "locator"}, (
                f"people_search.py reaches .{node.attr}"
            )
    for forbidden in ("browser", "dom", "playwright", "BROWSER", "server"):
        assert forbidden not in imported, f"people_search imports {forbidden}"


def test_compose_takes_exactly_the_tools_five_arguments() -> None:
    tree = _tree(MODULE)
    compose = next(n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name == "compose")
    assert [a.arg for a in compose.args.args] == []
    assert [a.arg for a in compose.args.kwonlyargs] == [
        "keywords", "current_company_ids", "past_company_ids",
        "location_ids", "connections_of",
    ]


def _tool_node() -> ast.AsyncFunctionDef:
    return next(
        node for node in _tree(SERVER).body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "linkedin_people_search_shape"
    )


def test_the_tool_hands_compose_its_own_parameters_and_nothing_else() -> None:
    tool = _tool_node()
    params = [a.arg for a in tool.args.args]
    calls = [
        node for node in ast.walk(tool)
        if isinstance(node, ast.Call)
        and ast.unparse(node.func) == "people_search.compose"
    ]
    assert len(calls) == 1, "exactly one composition per call"
    call = calls[0]
    assert not call.args, "compose is called by keyword only"
    passed = {kw.arg: kw.value for kw in call.keywords}
    assert sorted(passed) == sorted(params)
    for name, value in passed.items():
        assert isinstance(value, ast.Name) and value.id == name, (
            f"compose({name}=...) is handed {ast.unparse(value)}, not the "
            "tool's own parameter of that name"
        )


def test_the_tool_navigates_only_to_the_composed_address_by_its_source() -> None:
    tool = _tool_node()
    gotos = [
        node for node in ast.walk(tool)
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "BROWSER.goto"
    ]
    assert len(gotos) == 1
    assert ast.unparse(gotos[0].args[1]) == "composed['url']"


class _HostileSearchPage:
    """Answers every read with plants, the way the shipped hostile tests do."""

    def __init__(self) -> None:
        self.reads = 0

    async def evaluate(self, script: Any, arg: Any = None) -> Any:
        self.reads += 1
        return {
            "anchors": 12,
            "controls": 9,
            "counts": [PLANT] + [1] * 13,
            "decorated": [0] * 14,
            "queries_present": 1,
            "matched_controls": 9,
            "unmatched_controls": 3,
            "empty_labels": 1,
            "stray_label": "Connections of " + PLANT,
            "first_href": "/in/" + PLANTED_SLUG,
        }


class _RecordingBrowser:
    """Records every session and every navigation, and lands where it is told
    plus a query carrying a planted name and a planted facet value."""

    def __init__(self, landing_suffix: str = "") -> None:
        self.sessions = 0
        self.gotos: list[str] = []
        self.page = _HostileSearchPage()
        self.landing_suffix = landing_suffix

    def session(self):
        @contextlib.asynccontextmanager
        async def _session():
            self.sessions += 1
            yield self.page

        return _session()

    async def goto(self, page: Any, url: str) -> str:
        readonly.assert_read_url(url)
        self.gotos.append(url)
        return url + self.landing_suffix


def _drive(monkeypatch, browser: _RecordingBrowser, **kwargs: Any) -> dict:
    from linkedin_server import server

    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(search_results, "PANEL_POLL_MS", 0)
    return asyncio.run(server.linkedin_people_search_shape(**kwargs))


ALL_ARGUMENTS = {
    "keywords": MARKER_KEYWORD,
    "current_company_ids": ORG_A,
    "past_company_ids": ORG_B,
    "location_ids": GEO_A + "," + GEO_B,
    "connections_of": TOKEN_A,
}

#: The landing LinkedIn could legitimately choose: our query, plus its own
#: parameters carrying a name and a stranger's facet value.
HOSTILE_SUFFIX = (
    "&sid=" + PLANTED_SLUG
    + "&keywords=" + PLANT.replace(" ", "%20")
    + "&connectionOf=%5B%22" + TOKEN_B + "%22%5D"
)


def _assert_only_the_composed_address(gotos: list[str], expected: str) -> None:
    assert gotos == [expected], (
        f"the tool navigated to {len(gotos)} address(es); only the composed "
        "one may be opened, and nothing the page or the landing chose"
    )


def test_the_tool_navigates_only_to_the_composed_address_when_driven(monkeypatch) -> None:
    browser = _RecordingBrowser(landing_suffix=HOSTILE_SUFFIX)
    payload = _drive(monkeypatch, browser, **ALL_ARGUMENTS)
    assert payload["ok"] is True, payload
    _assert_only_the_composed_address(
        browser.gotos, people_search.compose(**ALL_ARGUMENTS)["url"]
    )
    assert browser.page.reads >= 2, "the page was not read at all"


def test_THIS_CONTROL_CAN_FAIL_the_recorder_convicts_a_second_navigation() -> None:
    expected = people_search.compose(**ALL_ARGUMENTS)["url"]
    with pytest.raises(AssertionError):
        _assert_only_the_composed_address([expected, expected + HOSTILE_SUFFIX], expected)
    with pytest.raises(AssertionError):
        _assert_only_the_composed_address([expected + HOSTILE_SUFFIX], expected)


def _carried(payload: Any, needles: tuple[str, ...]) -> list[str]:
    return [where for where, text in walk(payload)
            if any(needle in text for needle in needles)]


def test_the_driven_tool_publishes_no_plant_and_echoes_no_argument(monkeypatch) -> None:
    browser = _RecordingBrowser(landing_suffix=HOSTILE_SUFFIX)
    payload = _drive(monkeypatch, browser, **ALL_ARGUMENTS)
    assert not _carried(payload, PLANTS), _carried(payload, PLANTS)
    echoes = (MARKER_KEYWORD, ORG_A, ORG_B, TOKEN_A, TOKEN_B, "geoUrn=", "%5B")
    assert not _carried(payload, echoes), _carried(payload, echoes)
    assert payload["denominators"]["values_refused"] >= 1


def test_the_driven_tool_reports_what_linkedin_kept_as_literals(monkeypatch) -> None:
    browser = _RecordingBrowser(landing_suffix=HOSTILE_SUFFIX)
    payload = _drive(monkeypatch, browser, **ALL_ARGUMENTS)
    assert payload["query_applied"] == {
        "keywords": 1, "current_company_ids": 1, "past_company_ids": 1,
        "location_ids": 2, "connections_of": 1,
    }
    kept = payload["query_kept"]
    assert set(kept.values()) <= set(people_search.KEPT_VERDICTS)
    # The hostile landing REPEATED two keys with foreign values: neither may
    # read as kept.
    assert kept["keywords"] == "different_values"
    assert kept["connections_of"] == "different_values"
    assert kept["current_company_ids"] == "verbatim"
    assert payload["landed_where_it_was_sent"] is False
    assert payload["landed_on_people_search"] is True


def test_a_boundary_refusal_opens_no_session_and_loads_nothing(monkeypatch) -> None:
    browser = _RecordingBrowser()
    payload = _drive(monkeypatch, browser, keywords="exampleperson password")
    assert browser.sessions == 0 and browser.gotos == []
    assert payload["ok"] is False
    assert payload["error"] == "refused_by_the_read_boundary"
    assert payload["forbidden_substring"] == "password"
    assert payload["arguments_carrying_it"] == ["keywords"]
    assert payload["pages_loaded"] == 0
    assert not _carried(payload, ("exampleperson",))


def test_an_argument_refusal_opens_no_session_and_loads_nothing(monkeypatch) -> None:
    browser = _RecordingBrowser()
    payload = _drive(monkeypatch, browser, connections_of="example-person-1a2b")
    assert browser.sessions == 0 and browser.gotos == []
    assert payload["error"] == "bad_argument"
    assert payload["argument"] == "connections_of"
    assert not _carried(payload, ("example-person-1a2b",))


def test_the_no_argument_call_is_the_call_it_always_was(monkeypatch) -> None:
    browser = _RecordingBrowser()
    payload = _drive(monkeypatch, browser)
    assert browser.gotos == [search_results.PEOPLE_SEARCH_URL]
    assert payload["landed_where_it_was_sent"] is True
    assert payload["query_kept"] == {}
    assert set(payload["query_applied"].values()) == {0}


# ---------------------------------------------------------------------------
# 6. The landing verdict: a closed alphabet, and the landing never leaves
# ---------------------------------------------------------------------------

ASKED = _composed(keywords="senior engineer", current_company_ids=ORG_A,
                  location_ids=GEO_A + "," + GEO_B)


@pytest.mark.parametrize(
    "suffix_or_landing, expected",
    [
        # LinkedIn appends its own parameters: every argument verbatim.
        ("&origin=FACETED_SEARCH&sid=abc",
         {"keywords": "verbatim", "current_company_ids": "verbatim",
          "location_ids": "verbatim"}),
    ],
)
def test_a_landing_that_keeps_the_query_reads_verbatim(suffix_or_landing, expected) -> None:
    verdict = people_search.landing_verdict(ASKED + suffix_or_landing, ASKED)
    assert verdict == {"on_people_search": True, "query_kept": expected}


def test_a_rewritten_spelling_carrying_the_same_values_reads_same_values() -> None:
    landed = (
        search_results.PEOPLE_SEARCH_URL
        + "?" + urlencode([("keywords", "Senior  Engineer"),
                           ("currentCompany", ORG_A),
                           ("geoUrn", '["200","100"]')])
    )
    verdict = people_search.landing_verdict(landed, ASKED)
    assert verdict["query_kept"] == {
        "keywords": "same_values",
        "current_company_ids": "same_values",
        "location_ids": "same_values",
    }


def test_a_dropped_or_changed_value_is_never_read_as_kept() -> None:
    landed = (
        search_results.PEOPLE_SEARCH_URL
        + "?" + urlencode([("keywords", "director"), ("geoUrn", '["100"]')])
    )
    verdict = people_search.landing_verdict(landed, ASKED)
    assert verdict["query_kept"] == {
        "keywords": "different_values",
        "current_company_ids": "absent",
        "location_ids": "different_values",
    }


@pytest.mark.parametrize(
    "landing",
    [
        "https://www.linkedin.com/search/results/all/?keywords=senior+engineer",
        "https://www.linkedin.com/authwall?sessionRedirect=x",
        "https://example.invalid/search/results/people/",
        "https://www.linkedin.com/search/results/people/../../feed/",
        "",
        None,
    ],
)
def test_off_the_people_vertical_reads_false(landing) -> None:
    assert people_search.landing_verdict(landing, ASKED)["on_people_search"] is False


def test_the_verdict_carries_no_landed_value_whatever_the_landing_holds() -> None:
    landed = ASKED + HOSTILE_SUFFIX + "&geoUrn=%5B%22" + PLANTED_SLUG + "%22%5D"
    verdict = people_search.landing_verdict(landed, ASKED)
    assert not _carried(verdict, PLANTS)
    strings = [text for where, text in walk(verdict) if not where.endswith("(key)")]
    assert set(strings) <= set(people_search.KEPT_VERDICTS)


def test_an_unparseable_landing_reads_unreadable_not_a_guess() -> None:
    verdict = people_search.landing_verdict("https://[::1", ASKED)
    assert verdict["on_people_search"] is False
    assert set(verdict["query_kept"].values()) == {"unreadable"}


# ---------------------------------------------------------------------------
# 7. The census: the seven rows claim the coverage they were built with
# ---------------------------------------------------------------------------

_ROW = re.compile(r"^\|\s*(\d+)\s*\|[^|]*\|\s*R\s*\|\s*\*{0,2}([A-Z-]+)\*{0,2}\s*\|(.*)$")


def _network_rows() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for line in NETWORK.read_text(encoding="utf-8").splitlines():
        found = _ROW.match(line)
        if found:
            out.setdefault(found.group(1), (found.group(2), found.group(3)))
    return out


def test_the_census_walk_reads_the_slice_at_all() -> None:
    rows = _network_rows()
    assert len(rows) >= 50
    assert set(ROWS) <= set(rows)


@pytest.mark.parametrize("row", ROWS)
def test_the_row_claims_the_coverage_it_was_built_with(row: str) -> None:
    """GAP -> COVERED-UNFIRED, 2026-09-24. A fire that promotes or demotes the
    row must move this in the same commit."""
    state, note = _network_rows()[row]
    assert state == "COVERED-UNFIRED", (row, state)
    assert "linkedin_people_search_shape" in note
    assert "people_search" in note


_CHAIN = {
    "people_search.py": ("compose", "boundary_verdict", "landing_verdict",
                         "refusal_envelope"),
}


def _defined(source: str) -> set[str]:
    return {node.name for node in ast.walk(ast.parse(source))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def test_the_chain_the_rows_rest_on_is_whole() -> None:
    source = MODULE.read_text(encoding="utf-8")
    for name in _CHAIN["people_search.py"]:
        assert name in _defined(source), name
    keys = {key for _arg, key, _kind, _most in people_search.FACETS}
    assert keys == {"currentCompany", "pastCompany", "geoUrn", "connectionOf"}
    tool = _tool_node()
    assert [a.arg for a in tool.args.args] == [
        "keywords", "current_company_ids", "past_company_ids",
        "location_ids", "connections_of",
    ]


def test_THIS_CONTROL_CAN_FAIL_the_chain_check_convicts_a_renamed_function() -> None:
    source = MODULE.read_text(encoding="utf-8")
    mutated = source.replace("def compose(", "def compose_renamed(")
    assert mutated != source
    assert "compose" not in _defined(mutated)
