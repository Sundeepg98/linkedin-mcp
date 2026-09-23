"""THE FOUR-WORD SEARCH ADMISSION, AND THE COMPOSER FOR ITS THREE NEW WORDS.

``D2-SEARCH-VERTICALS-WIDENED`` (the orchestrator's delegated call,
2026-09-24) widened ``readonly._ALLOWED_URL_PATTERNS``'s people line to the
closed alternation ``/search/results/(people|companies|groups|events)/``. The
order that landed it asked for three things to be tested, and they are the
first three sections below:

1. EVERY ADMITTED SPELLING -- each word, with and without its slash, with and
   without a query, and every address ``search_verticals.compose`` builds.
2. THE ACCOUNT-ENDING TRAVERSAL from the 2026-09-19 preconditions measurement
   STILL REFUSED -- from all four words, not only the one that measured it.
3. A PLANTED PREFIX SPELLING REFUSED -- words that begin with an admitted word
   and are not one of them, deep paths under a word, and a changed case --
   with the control that a `/search/results/` PREFIX admits every one of
   them, so the refusals are the closed alternation's doing.

Then the composer: its refusals, its purity, and the fact the rest of this
change rests on -- that NOTHING in the package calls it and the one search
tool composes the people vertical only (section 5). See
``search_verticals.py`` for why that is condition 1 of the search admission
rather than an unfinished wire.

**MEASURED WITH ``is_read_url`` ON CONCRETE ADDRESSES**, never a substring
grep over the pattern list, which is the rule the search admission's
condition 3 set.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from linkedin_server import people_search, readonly, search_verticals  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "linkedin_server"
MODULE = PKG / "search_verticals.py"
SERVER = PKG / "server.py"

BASE = "https://www.linkedin.com"
WORDS = ("people", "companies", "groups", "events")


# ---------------------------------------------------------------------------
# 1. Every admitted spelling
# ---------------------------------------------------------------------------

def _spellings(word: str) -> list[str]:
    return [
        f"{BASE}/search/results/{word}/",
        f"{BASE}/search/results/{word}",
        f"{BASE}/search/results/{word}/?keywords=x",
        f"{BASE}/search/results/{word}?keywords=x",
        f"{BASE}/search/results/{word}/?keywords=two+words",
        f"{BASE}/search/results/{word}/?keywords=x&origin=SWITCH_SEARCH_VERTICAL",
    ]


@pytest.mark.parametrize("word", WORDS)
def test_every_spelling_of_every_admitted_word_is_admitted(word):
    refused = [url for url in _spellings(word) if not readonly.is_read_url(url)]
    assert refused == [], f"{word}: {refused}"


#: Keywords a person might search a company, a group or an event by, none of
#: which trips a forbidden substring. Written for their SHAPE: spaces,
#: punctuation, a hash, a slash, an ampersand, a quote and three scripts.
#: INVENTED; none names a real organisation, group or event.
KEYWORD_CORPUS = (
    "robotics",
    "open source maintainers",
    "c++ & rust",
    "#hiring",
    "a/b testing",
    "quality \"assurance\"",
    "\u0928\u092e\u0938\u094d\u0924\u0947",
    "\u00e9v\u00e9nements",
    "data  engineering  meetup",
)


@pytest.mark.parametrize("vertical", search_verticals.VERTICALS)
@pytest.mark.parametrize("keywords", KEYWORD_CORPUS)
def test_every_address_the_composer_builds_is_admitted(vertical, keywords):
    verdict = search_verticals.compose(vertical, keywords=keywords)
    assert verdict["built"] is True, verdict
    assert readonly.is_read_url(verdict["url"]) is True, verdict["url"]
    assert verdict["url"].startswith(f"{BASE}/search/results/{vertical}/?keywords=")


def test_the_corpus_is_ascii_in_this_source_file():
    """The non-ASCII keywords above are written as escapes. A file-writing
    tool once decoded escapes like these into literal characters in this
    repository; the byte scan is the measurement, not the intention."""
    MODULE_BYTES = pathlib.Path(__file__).read_bytes()
    assert all(byte < 128 for byte in MODULE_BYTES)


# ---------------------------------------------------------------------------
# 2. The account-ending traversal, still refused, from all four words
# ---------------------------------------------------------------------------

#: The 2026-09-19 preconditions measured the first spelling ADMITTED under
#: both family wildcards, named by no forbidden substring. The others are its
#: siblings from the same table and from the groups entry's traversal set.
TRAVERSAL_TAILS = (
    "../../mypreferences/d/close-account",
    "../../psettings/close-account",
    "../../mynetwork/invite-connect/invitations/",
    "../../in/someone-else/",
    "./",
    "../",
    "%2e%2e/%2e%2e/mypreferences/d/close-account",
)


@pytest.mark.parametrize("word", WORDS)
@pytest.mark.parametrize("tail", TRAVERSAL_TAILS)
def test_the_account_ending_traversal_is_still_refused(word, tail):
    url = f"{BASE}/search/results/{word}/{tail}"
    assert readonly.is_read_url(url) is False, url


# ---------------------------------------------------------------------------
# 3. A planted prefix spelling is refused -- and the control
# ---------------------------------------------------------------------------

#: Spellings that START with an admitted word, or sit under one, and are not
#: the page the ruling admitted. A prefix pattern admits every one of them.
PLANTED_PREFIX_SPELLINGS = (
    f"{BASE}/search/results/peoplefinder/",
    f"{BASE}/search/results/people-directory/?keywords=x",
    f"{BASE}/search/results/companiesx/?keywords=x",
    f"{BASE}/search/results/companies-hiring/",
    f"{BASE}/search/results/groupsearch/?keywords=x",
    f"{BASE}/search/results/groups_all/",
    f"{BASE}/search/results/eventsx/",
    f"{BASE}/search/results/events2/?keywords=x",
    f"{BASE}/search/results/companies/12345/",
    f"{BASE}/search/results/groups/example-group/",
    f"{BASE}/search/results/events/extra/?keywords=x",
    f"{BASE}/search/results/Companies/?keywords=x",
    f"{BASE}/search/results/GROUPS/",
    f"{BASE}/search/results/xpeople/",
    f"{BASE}/search/results//companies/",
)


@pytest.mark.parametrize("url", PLANTED_PREFIX_SPELLINGS)
def test_a_planted_prefix_spelling_is_refused(url):
    assert readonly.is_read_url(url) is False, url


def test_control_a_results_prefix_admits_every_planted_spelling():
    """SHOWN FAILING. Install the prefix condition 2 forbids and every planted
    spelling above goes True -- so each refusal above is the closed
    alternation's work, and none is an accident of a forbidden substring."""
    original = readonly._ALLOWED_URL_PATTERNS
    readonly._ALLOWED_URL_PATTERNS = original + (
        re.compile(r"^https://www\.linkedin\.com/search/results/"),
    )
    try:
        admitted = [u for u in PLANTED_PREFIX_SPELLINGS if readonly.is_read_url(u)]
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    assert admitted == list(PLANTED_PREFIX_SPELLINGS)
    assert not any(readonly.is_read_url(u) for u in PLANTED_PREFIX_SPELLINGS)


def test_exactly_one_pattern_admits_each_word():
    """The widening EDITED the people line; it did not add a second search
    entry. Each word is matched by exactly one pattern on the allowlist."""
    for word in WORDS:
        url = f"{BASE}/search/results/{word}/?keywords=x"
        matching = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]
        assert len(matching) == 1, (word, [p.pattern for p in matching])


# ---------------------------------------------------------------------------
# 4. The composer
# ---------------------------------------------------------------------------

def test_the_composer_composes_exactly_the_three_new_words():
    assert search_verticals.VERTICALS == ("companies", "groups", "events")
    assert set(search_verticals.ROWS_SERVED) == set(search_verticals.VERTICALS)
    assert sorted(r for rows in search_verticals.ROWS_SERVED.values() for r in rows) \
        == ["M C70", "N 104", "N 161", "N 179"]


@pytest.mark.parametrize("vertical", ["people", "content", "all", "Companies",
                                      "companies/", "", None, 7])
def test_any_other_vertical_is_refused_and_not_quoted(vertical):
    verdict = search_verticals.compose(vertical, keywords="robotics")
    assert verdict["built"] is False
    assert verdict["refused"] == "not_a_d2_vertical"
    assert verdict["argument"] == "vertical"
    assert "url" not in verdict


def test_the_people_vertical_is_pointed_at_its_own_composer():
    verdict = search_verticals.compose("people", keywords="robotics")
    assert "people_search.compose" in verdict["why"]


@pytest.mark.parametrize("keywords", ["", "   ", None])
def test_a_keyword_is_required(keywords):
    verdict = search_verticals.compose("groups", keywords=keywords)
    assert verdict == {
        "built": False,
        "argument": "keywords",
        "refused": "keywords_required",
        "saw": verdict["saw"],
        "why": verdict["why"],
    }


@pytest.mark.parametrize("keywords, refused", [
    ("x" * (people_search.MAX_KEYWORD_CHARS + 1), "keywords_too_long"),
    ("line one\nline two", "keywords_carry_a_control_character"),
    ("tab\there", "keywords_carry_a_control_character"),
])
def test_a_bad_keyword_gets_the_people_searchs_own_refusal(keywords, refused):
    """THE SAME CODE, NOT A COPY: the refusal is the one people_search.compose
    returns for the same keyword, field for field."""
    ours = search_verticals.compose("events", keywords=keywords)
    theirs = people_search.compose(keywords=keywords)
    assert ours["refused"] == refused
    assert ours == theirs


def test_a_rejected_value_is_described_and_never_quoted():
    """The control character sits INSIDE the value: a trailing one is stripped
    with the surrounding whitespace, and the value is then a valid keyword --
    which is what this test's first draft planted, and it passed nothing."""
    marker = "Zyxwvut Qponmlk"
    verdict = search_verticals.compose("companies", keywords=marker + "\nx")
    assert verdict["built"] is False
    assert verdict["refused"] == "keywords_carry_a_control_character"
    assert marker not in repr(verdict)


def test_the_keyword_is_encoded_exactly_as_the_people_search_encodes_it():
    ours = search_verticals.compose("companies", keywords="c++ & rust")["url"]
    theirs = people_search.compose(keywords="c++ & rust")["url"]
    assert ours.split("?", 1)[1] == theirs.split("?", 1)[1]


def test_a_keyword_that_trips_a_forbidden_substring_is_refused_by_the_door():
    """B.4 of the 2026-09-19 preconditions, on the new words: the composer
    builds the address and the boundary refuses it, exactly as it does for the
    people search. The denylist is not narrowed for any vertical."""
    verdict = search_verticals.compose("groups", keywords="invitation")
    assert verdict["built"] is True
    assert readonly.is_read_url(verdict["url"]) is False
    assert people_search.boundary_verdict(verdict["url"])["boundary_refusal"] \
        == "FORBIDDEN"


def _tree(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def test_the_composer_touches_no_page_and_no_browser():
    """The structural half of the derivation proof, off the module's AST."""
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
            assert not isinstance(node, ast.AsyncFunctionDef), node.name
        elif isinstance(node, ast.Attribute):
            assert node.attr not in {"goto", "evaluate", "content", "locator",
                                     "click", "press", "mouse", "wheel"}, node.attr
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            raise AssertionError("the composer loops; it composes ONE address")
    for forbidden in ("browser", "dom", "playwright", "BROWSER", "server",
                      "anchors"):
        assert forbidden not in imported, f"search_verticals imports {forbidden}"


def test_compose_takes_a_vertical_and_a_keyword_and_nothing_else():
    tree = _tree(MODULE)
    compose = next(n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name == "compose")
    assert [a.arg for a in compose.args.args] == ["vertical"]
    assert [a.arg for a in compose.args.kwonlyargs] == ["keywords"]


# ---------------------------------------------------------------------------
# 5. Nothing opens the three new words yet -- condition 1, held by absence
# ---------------------------------------------------------------------------

def _imports_of(path: pathlib.Path) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "linkedin_server":
                out.update(alias.name for alias in node.names)
            elif module.startswith("linkedin_server."):
                out.add(module.split(".")[1])
            elif node.level and not module:
                out.update(alias.name for alias in node.names)
            elif node.level:
                out.add(module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == "linkedin_server" and len(parts) > 1:
                    out.add(parts[1])
    return out


def test_no_package_module_or_entry_point_imports_the_composer():
    """CONDITION 1 OF THE SEARCH ADMISSION, HELD BY ABSENCE. The first tool
    that imports this module must land with its name-free reader in the same
    commit, and delete the orphan ruling that says so."""
    importers = [
        path.name
        for path in sorted(PKG.glob("*.py")) + sorted(ROOT.glob("*.py"))
        if path.name != "search_verticals.py"
        and "search_verticals" in _imports_of(path)
    ]
    assert importers == [], importers


def test_control_the_import_walk_sees_a_real_import():
    """The walk above is not blind: it finds people_search imported by the
    server, which is the one search composer that IS wired."""
    assert "people_search" in _imports_of(SERVER)


def test_the_one_search_tool_composes_the_people_vertical_only():
    """Every search-results address the server can open is composed by
    ``people_search.compose``, whose base is the people vertical."""
    assert people_search.BASE_URL == f"{BASE}/search/results/people/"
    source = SERVER.read_text(encoding="utf-8")
    for word in ("companies", "groups", "events"):
        assert f"/search/results/{word}" not in source, word
    assert "search_verticals" not in source
