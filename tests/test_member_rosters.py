"""MEMBER ROSTERS AS BOUNDED READS: the four roster lines, and a test per condition.

``MEMBER-ROSTERS-AS-BOUNDED-READS`` (the orchestrator's delegated call,
2026-09-24) admits a roster the operator can open himself -- a group's members,
an event's attendees, a company's or a school's People tab -- under five
conditions. The order that landed the admission asked for tests that PROVE
each one, and this file is organised by them:

    1  one page per call, no automatic pagination     section 2
       -- including a PLANTED PAGINATION LOOP that must be refused
    2  the id from the tool's arguments only           section 3
       -- and the navigation-derivation guard green over the new code
    3  no member's name or id in a tracked file        section 4
    4  inside the live budget                          section 5
    5  the rows become GAP, blocked on a reader        the census, and
                                                       section 6 here

Section 1 is the admission itself: exactly one line per roster, the blast
radius of each line measured with the shipped instrument, and the neighbours
that stay refused.

Every id below is invented: repdigits and runs that name nothing.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402
from linkedin_server import member_rosters, readonly  # noqa: E402

PKG = ROOT / "linkedin_server"
MODULE = PKG / "member_rosters.py"
BASE = "https://www.linkedin.com"

GROUP_ID = "12345678"
EVENT_ID = "7777777777777777777"
ORG_ID = "5417062"
SCHOOL_ID = "1111111"
SLUG = "a-company"
SCHOOL_SLUG = "example-university"

#: ``roster -> (the address compose builds for the invented id, the carrier
#: fragment that names its line)``.
COMPOSED = {
    "group_members": (f"{BASE}/groups/{GROUP_ID}/members/", "/members/?$"),
    "event_attendees": (f"{BASE}/events/{EVENT_ID}/attendees/", "/attendees/?$"),
    "company_people": (f"{BASE}/company/{ORG_ID}/people/", "com/company/"),
    "school_people": (f"{BASE}/school/{SCHOOL_ID}/people/", "com/school/"),
}
IDS = {
    "group_members": GROUP_ID,
    "event_attendees": EVENT_ID,
    "company_people": ORG_ID,
    "school_people": SCHOOL_ID,
}


def _carriers(url: str) -> list:
    return [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]


# ---------------------------------------------------------------------------
# 1. The admission: one line per roster, and nothing next door
# ---------------------------------------------------------------------------

#: What each roster line was admitted for. Groups and events: the numeric id
#: only, as their id entries are. Company and school: the slug form as well,
#: because LinkedIn DRAWS the People tab by slug (two captures in the
#: gitignored ``_state/``, counted by shape) and the ``/company/`` root
#: entry's argument about a numeric request landing on a slug arrival applies
#: unchanged -- but WITHOUT ``%`` in the class; see
#: ``ENCODED_PEOPLE_TAB_SPELLINGS``.
ADMITTED = {
    "group_members": (
        f"{BASE}/groups/{GROUP_ID}/members/",
        f"{BASE}/groups/{GROUP_ID}/members",
    ),
    "event_attendees": (
        f"{BASE}/events/{EVENT_ID}/attendees/",
        f"{BASE}/events/{EVENT_ID}/attendees",
    ),
    "company_people": (
        f"{BASE}/company/{ORG_ID}/people/",
        f"{BASE}/company/{ORG_ID}/people",
        f"{BASE}/company/{SLUG}/people/",
        f"{BASE}/company/{SLUG}/people",
    ),
    "school_people": (
        f"{BASE}/school/{SCHOOL_ID}/people/",
        f"{BASE}/school/{SCHOOL_ID}/people",
        f"{BASE}/school/{SCHOOL_SLUG}/people/",
        f"{BASE}/school/{SCHOOL_SLUG}/people",
    ),
}

#: The neighbours every roster line must leave shut. The QUERY and PAGE
#: spellings are condition 1's; the rest are the family a wider line would
#: sweep in.
NEIGHBOURS = (
    # a slug where the family is numeric-only
    f"{BASE}/groups/example-group/members/",
    f"{BASE}/events/some-event-placeholder-{EVENT_ID}/attendees/",
    # non-ASCII digits and an over-long run
    f"{BASE}/groups/\u0661\u0662\u0663/members/",
    f"{BASE}/events/\uff11\uff12\uff13/attendees/",
    f"{BASE}/groups/{'1' * 21}/members/",
    f"{BASE}/company/{'1' * 101}/people/",
    # deeper paths under a roster -- a member reached THROUGH the roster
    f"{BASE}/groups/{GROUP_ID}/members/someone-else/",
    f"{BASE}/company/{SLUG}/people/in/someone-else/",
    f"{BASE}/school/{SCHOOL_SLUG}/people/someone-else/",
    f"{BASE}/events/{EVENT_ID}/attendees/someone-else/",
    # the group's other queues
    f"{BASE}/groups/{GROUP_ID}/requests/",
    f"{BASE}/groups/{GROUP_ID}/members/manage/",
    f"{BASE}/groups/{GROUP_ID}/members/invite/",
    # traversals, including onto a member profile and an account ending
    f"{BASE}/groups/{GROUP_ID}/members/../../../in/someone-else/",
    f"{BASE}/company/{SLUG}/people/../../../mypreferences/d/close-account",
    f"{BASE}/school/{SCHOOL_SLUG}/people/../../../in/someone-else/",
    f"{BASE}/events/{EVENT_ID}/attendees/../../../psettings/close-account",
    f"{BASE}/company/a.company/people/",
    f"{BASE}/company/a..company/people/",
    # a case change, and the tab word glued on
    f"{BASE}/groups/{GROUP_ID}/Members/",
    f"{BASE}/company/{SLUG}/peoplex/",
    f"{BASE}/events/{EVENT_ID}/attendeesx/",
)

#: CONDITION 1's spellings: a second page, however it might be asked for.
PAGINATION = (
    "?page=2",
    "?start=25",
    "?count=100",
    "?offset=50",
    "?page=2&keywords=x",
    "?facetConnectionOf=1",
    "?keywords=x",
    "page/2/",
    "2/",
)


def _page_spellings(url: str) -> list[str]:
    base = url if url.endswith("/") else url + "/"
    return [base + tail for tail in PAGINATION] + [base.rstrip("/") + tail
                                                   for tail in PAGINATION
                                                   if tail.startswith("?")]


@pytest.mark.parametrize("roster", sorted(ADMITTED))
def test_each_roster_address_is_admitted_by_exactly_one_line(roster):
    for url in ADMITTED[roster]:
        carriers = _carriers(url)
        assert readonly.is_read_url(url), url
        assert len(carriers) == 1, (url, [p.pattern for p in carriers])


def test_the_four_rosters_are_four_distinct_lines():
    lines = {_carriers(urls[0])[0].pattern for urls in ADMITTED.values()}
    assert len(lines) == 4, lines


@pytest.mark.parametrize("url", NEIGHBOURS)
def test_the_neighbours_stay_refused(url):
    assert readonly.is_read_url(url) is False, url


#: ENCODED SPELLINGS OF A PEOPLE TAB, added after this follow-up's cold
#: verification ADMITTED the first five through the People-tab lines as they
#: first shipped, with ``%`` in their class. The URL standard reads ``%2e``
#: and ``%2e%2e`` as ``.`` and ``..``, so those land on ``/company/people/``
#: and ``/people/``; the rest are encoded characters no composer here builds.
#: The 197-address corpus above held literal dots only, which is how the
#: blast-radius test could pass while this class was open.
ENCODED_PEOPLE_TAB_SPELLINGS = tuple(
    f"{BASE}/{word}/{segment}/people/"
    for word in ("company", "school")
    for segment in ("%2e", "%2E", "%2e%2e", "%2E%2E", "%2e%2E", "a%2Fb",
                    "a%2fb", "a-company%3Bx", "%2e%2e%2e", "a%2e",
                    "soci%C3%A9t%C3%A9")
)


@pytest.mark.parametrize("url", ENCODED_PEOPLE_TAB_SPELLINGS)
def test_no_encoded_spelling_of_a_people_tab_is_admitted(url):
    assert readonly.is_read_url(url) is False, url


def test_control_the_root_entries_class_would_admit_the_encoded_dot():
    """SHOWN FAILING: put the root entries' class -- ``%`` included -- back on
    the company People-tab line, and the encoded ``..`` goes through. So the
    refusal above is the narrower class, not an accident."""
    line = _carriers(f"{BASE}/company/{ORG_ID}/people/")[0]
    wider = re.compile(
        r"^https://www\.linkedin\.com/company/[A-Za-z0-9%\-_]{1,100}/people/?$")
    original = readonly._ALLOWED_URL_PATTERNS
    readonly._ALLOWED_URL_PATTERNS = tuple(
        wider if p is line else p for p in original)
    try:
        assert readonly.is_read_url(f"{BASE}/company/%2e%2e/people/") is True
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    assert readonly.is_read_url(f"{BASE}/company/%2e%2e/people/") is False


def _corpus() -> list[str]:
    extra = {u for urls in ADMITTED.values() for u in urls}
    extra |= set(NEIGHBOURS)
    for urls in ADMITTED.values():
        for url in urls:
            extra |= set(_page_spellings(url))
    return sorted(set(blast_radius.corpus()) | extra)


@pytest.mark.parametrize("roster", sorted(ADMITTED))
def test_each_line_newly_admits_exactly_its_own_addresses(roster):
    """THE BLAST RADIUS, measured with the SHIPPED instrument: the line is
    taken out and handed back as a candidate over the shipped corpus plus
    every spelling in this file. What it newly admits must be exactly its own
    addresses -- no page spelling, no query, no neighbour."""
    line = _carriers(ADMITTED[roster][0])[0]
    original = readonly._ALLOWED_URL_PATTERNS
    try:
        readonly._ALLOWED_URL_PATTERNS = tuple(p for p in original if p is not line)
        result = blast_radius.newly_admitted(line.pattern, _corpus())
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    shipped_corpus_same_family = {
        u for u in blast_radius.corpus() if line.match(u)
        and not any(bad in u.lower() for bad in readonly._FORBIDDEN_URL_SUBSTRINGS)
    }
    expected = set(ADMITTED[roster]) | shipped_corpus_same_family
    assert sorted(result["newly_admitted"]) == sorted(expected)
    assert result["newly_refused"] == []


# ---------------------------------------------------------------------------
# 2. CONDITION 1 -- one page per call, no automatic pagination
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("roster", sorted(ADMITTED))
def test_no_second_page_is_admitted_however_it_is_spelled(roster):
    admitted = [u for url in ADMITTED[roster] for u in _page_spellings(url)
                if readonly.is_read_url(u)]
    assert admitted == [], admitted


@pytest.mark.parametrize("roster", sorted(COMPOSED))
def test_a_planted_pagination_loop_is_refused_at_its_second_step(roster):
    """THE PLANTED LOOP. A paginator is written here, in this test, the way a
    future reader might be tempted to write one: take the composed first page
    and walk ``?page=2``, ``?page=3`` ... through the SHIPPED boundary's
    raising form. The first step passes; every later step is refused, so no
    loop of this shape can get past one page through ``BROWSER.goto``."""
    first = member_rosters.compose(roster, IDS[roster])["url"]
    readonly.assert_read_url(first)
    refused = 0
    for number in range(2, 6):
        for spelling in (f"{first}?page={number}", f"{first}?start={25 * (number - 1)}"):
            with pytest.raises(readonly.WriteAttemptError):
                readonly.assert_read_url(spelling)
            refused += 1
    assert refused == 8


def test_control_a_query_admitting_roster_line_lets_the_loop_through():
    """SHOWN FAILING: install the obvious wider line -- the group roster WITH
    a query -- and the planted loop's second step is admitted. So the refusal
    above is the roster line's closed spelling, not an accident."""
    first = member_rosters.compose("group_members", GROUP_ID)["url"]
    original = readonly._ALLOWED_URL_PATTERNS
    readonly._ALLOWED_URL_PATTERNS = original + (
        re.compile(r"^https://www\.linkedin\.com/groups/[0-9]{1,20}/members/?(\?[^#]*)?$"),
    )
    try:
        assert readonly.is_read_url(f"{first}?page=2") is True
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    assert readonly.is_read_url(f"{first}?page=2") is False


def test_compose_takes_a_roster_and_an_id_and_nothing_else():
    """No page, offset or count argument exists to ask for a second page."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    compose = next(n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name == "compose")
    assert [a.arg for a in compose.args.args] == ["roster", "identifier"]
    assert compose.args.kwonlyargs == [] and compose.args.vararg is None
    assert compose.args.kwarg is None


@pytest.mark.parametrize("roster", sorted(COMPOSED))
def test_one_call_is_one_address(roster):
    verdict = member_rosters.compose(roster, IDS[roster])
    assert verdict["built"] is True
    assert verdict["url"] == COMPOSED[roster][0]
    assert verdict["loads"] == member_rosters.LOADS_PER_CALL == 1
    assert readonly.is_read_url(verdict["url"])


#: What a pagination or navigation would need in this module. None may appear.
_NAVIGATING_ATTRIBUTES = frozenset({
    "goto", "click", "press", "tap", "dispatch_event", "evaluate", "content",
    "locator", "mouse", "wheel", "keyboard", "scroll_into_view_if_needed",
    "fill", "type", "reload", "go_back", "go_forward",
})
_PAGE_SIDE_IMPORTS = frozenset({
    "browser", "BROWSER", "dom", "anchors", "server", "playwright", "press",
    "view_switch",
})


def pagination_findings(source: str) -> list[str]:
    """What in ``source`` could walk past one page or reach one at all.

    A roster composer needs none of: a loop, a comprehension, a coroutine, an
    await, a navigating attribute, or a page-side import. Returns one line per
    finding; empty is the only passing answer.
    """
    findings: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            findings.append(f"line {node.lineno}: a loop")
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp,
                               ast.GeneratorExp)):
            findings.append(f"line {node.lineno}: a comprehension")
        elif isinstance(node, (ast.AsyncFunctionDef, ast.Await)):
            findings.append(f"line {node.lineno}: async")
        elif isinstance(node, ast.Attribute) and node.attr in _NAVIGATING_ATTRIBUTES:
            findings.append(f"line {node.lineno}: .{node.attr}")
        elif isinstance(node, ast.ImportFrom):
            names = {node.module or ""} | {a.name for a in node.names}
            names |= {(node.module or "").split(".")[-1]}
            if names & _PAGE_SIDE_IMPORTS:
                findings.append(f"line {node.lineno}: imports {sorted(names & _PAGE_SIDE_IMPORTS)}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[-1] in _PAGE_SIDE_IMPORTS:
                    findings.append(f"line {node.lineno}: imports {alias.name}")
    return findings


def test_the_composer_can_walk_no_page_and_reach_none():
    assert pagination_findings(MODULE.read_text(encoding="utf-8")) == []


PLANTED_PAGINATORS = {
    "a for loop over page numbers": (
        "def more(first):\n"
        "    out = []\n"
        "    for n in range(2, 9):\n"
        "        out.append(first + '?page=' + str(n))\n"
        "    return out\n"
    ),
    "a while loop that navigates": (
        "async def walk(page, first):\n"
        "    url = first\n"
        "    while url:\n"
        "        await BROWSER.goto(page, url)\n"
        "        url = None\n"
    ),
    "a comprehension of pages": (
        "def pages(first):\n"
        "    return [first + '?start=' + str(25 * n) for n in range(1, 4)]\n"
    ),
    "a scroll": "def more(page):\n    page.mouse.wheel(0, 4000)\n",
    "a show-more press": (
        "def more(page):\n    page.locator('button').click()\n"
    ),
    "a page-side import": "from linkedin_server import dom\n",
}


@pytest.mark.parametrize("name", sorted(PLANTED_PAGINATORS))
def test_control_every_planted_paginator_is_convicted(name):
    """SHOWN FAILING: the module's own source with a paginator appended."""
    source = MODULE.read_text(encoding="utf-8") + "\n\n" + PLANTED_PAGINATORS[name]
    assert pagination_findings(source), name


# ---------------------------------------------------------------------------
# 3. CONDITION 2 -- the id from the tool's arguments only
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("roster", sorted(COMPOSED))
@pytest.mark.parametrize("bad, refused", [
    ("", "no_identifier"),
    ("example-group", "identifier_is_not_numeric"),
    ("a-company", "identifier_is_not_numeric"),
    # Built from the invented id rather than written out: a urn spelled with a
    # digit run in a tracked file is what the identity guard's urn shape
    # refuses, and the groups boundary test builds its urn the same way.
    (f"urn:li:group:{GROUP_ID}", "identifier_is_not_numeric"),
    ("12345678-placeholder", "identifier_is_not_numeric"),
    ("\u0661\u0662\u0663", "identifier_is_not_numeric"),
    ("\uff11\uff12\uff13", "identifier_is_not_numeric"),
    ("1" * 21, "identifier_too_long"),
])
def test_anything_but_a_bounded_digit_run_is_refused(roster, bad, refused):
    verdict = member_rosters.compose(roster, bad)
    assert verdict["built"] is False, verdict
    assert verdict["refused"] == refused, verdict
    assert verdict["argument"] == "identifier"
    assert "url" not in verdict


def test_a_refusal_describes_the_value_and_never_quotes_it():
    marker = "somebody-and-friends"
    for roster in COMPOSED:
        verdict = member_rosters.compose(roster, marker)
        assert marker not in repr(verdict), roster


def test_an_unknown_roster_is_refused():
    for name in ("people", "members", "", None, "group-members"):
        verdict = member_rosters.compose(name, GROUP_ID)
        assert verdict["built"] is False and verdict["refused"] == "not_a_roster"


@pytest.mark.parametrize("roster", ["group_members", "event_attendees"])
@pytest.mark.parametrize("segment", [
    GROUP_ID, "1", "9" * 20, "9" * 21, "example-group", "\u0661\u0662\u0663", "",
])
def test_the_composer_and_the_boundary_agree_on_the_numeric_rosters(roster, segment):
    """THE COUPLING, where both are numeric-only: the composer builds an
    address exactly when the boundary would admit it. A divergence either way
    is the defect the groups wave found on its first run."""
    path_word, tab_word, _rows = member_rosters.ROSTERS[roster]
    url = f"{BASE}/{path_word}/{segment}/{tab_word}/"
    assert member_rosters.compose(roster, segment)["built"] == readonly.is_read_url(url)


@pytest.mark.parametrize("roster", ["company_people", "school_people"])
def test_the_composer_is_stricter_than_the_boundary_on_a_slug(roster):
    """THE DOCUMENTED ASYMMETRY, in the safe direction: the boundary admits
    the People tab by slug because LinkedIn draws it that way; the composer
    assembles only the numeric form, because a slug is a name."""
    path_word, tab_word, _rows = member_rosters.ROSTERS[roster]
    slug_url = f"{BASE}/{path_word}/{SLUG}/{tab_word}/"
    assert readonly.is_read_url(slug_url) is True
    assert member_rosters.compose(roster, SLUG)["built"] is False


def _guard():
    spec = importlib.util.spec_from_file_location(
        "_nav_guard", ROOT / "tests" / "test_navigation_is_never_derived.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_navigation_derivation_guard_is_green_over_this_module():
    """Lane G's hardened guard -- a value a reader returned is a derived
    navigation too -- run over the composer's own source, both walks."""
    guard = _guard()
    source = MODULE.read_text(encoding="utf-8")
    assert guard.violations(source, "member_rosters.py") == []
    assert guard.output_violations(source, "member_rosters.py") == []
    assert guard.reader_derived_navigations(ast.parse(source)) == []


# ---------------------------------------------------------------------------
# 4. CONDITION 3 -- nothing stored in a tracked file
# ---------------------------------------------------------------------------

_WRITING_CALLS = frozenset({"open", "write_text", "write_bytes", "dump",
                            "dumps_to", "writelines", "write", "mkdir",
                            "touch", "savefig", "to_csv"})
_WRITING_MODULES = frozenset({"json", "pickle", "shelve", "sqlite3", "csv",
                              "pathlib", "os", "shutil", "tempfile", "io",
                              "logging"})


def storage_findings(source: str) -> list[str]:
    """Every way ``source`` could put a value on disk. Empty is passing."""
    findings: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in _WRITING_CALLS:
                findings.append(f"line {node.lineno}: {name}()")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _WRITING_MODULES:
                    findings.append(f"line {node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _WRITING_MODULES:
                findings.append(f"line {node.lineno}: from {node.module}")
    return findings


def test_the_composer_stores_nothing():
    assert storage_findings(MODULE.read_text(encoding="utf-8")) == []


PLANTED_STORES = {
    "a file write": "def keep(url):\n    open('roster.txt', 'w').write(url)\n",
    "a path write": "import pathlib\npathlib.Path('r.txt').write_text('x')\n",
    "a json dump": "import json\njson.dump({}, None)\n",
    "a log line": "import logging\nlogging.getLogger().info('x')\n",
}


@pytest.mark.parametrize("name", sorted(PLANTED_STORES))
def test_control_every_planted_store_is_convicted(name):
    source = MODULE.read_text(encoding="utf-8") + "\n\n" + PLANTED_STORES[name]
    assert storage_findings(source), name


# ---------------------------------------------------------------------------
# 5. CONDITION 4 -- inside the live budget
# ---------------------------------------------------------------------------

def test_a_roster_read_costs_one_load_and_the_budget_is_the_ruled_one():
    """One call is one load, so every roster read is countable against the
    live session's forty (``LIVE-BUDGET-40-LOADS``), exactly like any other
    load; the capture specs price each one.

    **WHAT THIS CANNOT DO, said so it is not read as more (the cold
    verification's point):** it cannot fail on a budget OVERRUN. Nothing in
    this package counts a session's loads -- the budget is carried by the live
    lane's process, as every other load's is. What code carries is the half
    this asserts: a roster read is exactly one load, with no loop that could
    make it more (section 2)."""
    assert member_rosters.LOADS_PER_CALL == 1
    register = (ROOT / "_audit" / "RULINGS.md").read_text(encoding="utf-8")
    assert "`LIVE-BUDGET-40-LOADS`" in register


# ---------------------------------------------------------------------------
# 6. Nothing opens a roster yet -- the rows stay GAP until a reader lands
# ---------------------------------------------------------------------------

def _orphan_walk():
    """The orphan test's own import reader, loaded rather than copied: it sees
    ``from . import x`` and ``from .x import y``, the relative forms four
    package modules use. The first version of this test had its own walk and
    was blind to both -- the cold verification planted them and it passed."""
    spec = importlib.util.spec_from_file_location(
        "_orphan_rule", ROOT / "tests" / "test_every_orphan_module_is_ruled.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._imported_submodules


def test_no_package_module_or_entry_point_imports_the_composer():
    imported_by = _orphan_walk()
    importers = [
        path.name
        for path in sorted(PKG.glob("*.py")) + sorted(ROOT.glob("*.py"))
        if path.name != "member_rosters.py"
        and "member_rosters" in imported_by(path)
    ]
    assert importers == [], importers


@pytest.mark.parametrize("line", [
    "from . import member_rosters\n",
    "from .member_rosters import compose\n",
    "from linkedin_server import member_rosters\n",
    "from linkedin_server.member_rosters import compose\n",
    "import linkedin_server.member_rosters\n",
])
def test_control_the_import_walk_sees_every_import_form(line, tmp_path):
    """SHOWN FAILING, on the five forms, relative ones included."""
    planted = tmp_path / "planted_module.py"
    planted.write_text(line, encoding="utf-8")
    assert "member_rosters" in _orphan_walk()(planted), line


def test_the_rows_each_roster_serves_are_the_rulings_and_the_address_tables():
    rows = sorted(r for _p, _t, rs in member_rosters.ROSTERS.values() for r in rs)
    assert rows == sorted(["N 165", "N 177", "N 188", "N 189", "J 108",
                           "N 102", "N 99", "N 100", "J 112"])
