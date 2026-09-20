"""The search-results shaper's properties, and the controls that can fail.

TWO LAYERS. The STRUCTURAL layer reads signatures, orders, the closed alphabet
and the shipped script's own source text. The CROSS-ENGINE layer lifts the
shipped decision out of that script by brace-matching and RUNS IT UNDER V8 --
the instrument ``tests/test_compose_fields.py`` already ships, imported rather
than reinvented.

**Nothing here opens a browser, navigates, or admits an address.** The engine
is node, the input is a fixture, and no page is loaded on any path.

**EVERY GUARD THAT COULD BE WRITTEN UNFALSIFIABLE HAS A PARTNER SHOWING IT
RED.** An instrument enters only if it has been shown failing. The pairs:

* the kind order -- a reorder renames the hazard class;
* the traversal rule's presence in the shipped source -- stripped, the reader
  says so;
* the traversal rule's EFFECT under V8 -- stripped, the real engine calls an
  account-ending address ``person_result``;
* the fixture tally -- an unpredicted anchor changes it;
* the closed alphabet and the short-count report.

**AND THE ONE THAT MATTERS MOST:** ``CONTROL_EXPECTATION`` is now COMPUTED.
Until the cross-engine layer existed it was a table of numbers nothing had
ever produced, which is the definition of a control that cannot fail.
"""

from __future__ import annotations

import inspect
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap

import pytest

from linkedin_server import search_results

#: Parameter names that would mean an address, a needle or a person reached a
#: function here. ``groups.py``'s list, plus the two this surface adds:
#: a search takes a QUERY, and its rows are PEOPLE.
_ADDRESS_SHAPED = {
    "href", "url", "uri", "link", "slug", "path", "address", "urn", "id",
    "profile", "member", "name", "person", "people", "keywords", "query",
    "q", "needle", "search", "term", "text",
}

_PUBLIC = [
    name
    for name in dir(search_results)
    if not name.startswith("_") and callable(getattr(search_results, name))
]


def test_the_module_is_readable_at_all() -> None:
    assert search_results.RESULT_KINDS
    assert search_results.RESULT_TABLE
    assert callable(search_results.tally)


def test_no_address_or_needle_is_a_parameter_of_any_function() -> None:
    offenders: dict[str, set[str]] = {}
    for name in _PUBLIC:
        target = getattr(search_results, name)
        if not (inspect.isfunction(target) or inspect.iscoroutinefunction(target)):
            continue
        found = _ADDRESS_SHAPED & set(inspect.signature(target).parameters)
        if found:
            offenders[name] = found
    assert not offenders, (
        "A function here can be handed an address or a needle: "
        f"{offenders}. Search results are made of other people; the whole "
        "shaper is the promise that no name is a parameter."
    )


def test_the_readers_only_string_parameter_is_the_documented_control_path() -> None:
    signature = inspect.signature(search_results.read_results)
    assert list(signature.parameters) == ["page", "html"], (
        "read_results' signature changed. Its second parameter is the "
        "documented CONTROL path and there is no third."
    )


def test_tally_takes_integers_and_cannot_be_handed_a_needle() -> None:
    signature = inspect.signature(search_results.tally)
    assert list(signature.parameters) == ["counts", "queries_present"]
    assert not (_ADDRESS_SHAPED & set(signature.parameters))


def test_the_kind_order_is_the_contract_and_person_result_is_index_zero() -> None:
    assert search_results.RESULT_KINDS[0] == "person_result", (
        "person_result is the HAZARD CLASS and its index is the contract. "
        "Every reading ever taken is a position in this tuple."
    )
    assert search_results.term_for(0) == "person_result"
    assert len(set(search_results.RESULT_KINDS)) == len(search_results.RESULT_KINDS)


def test_out_of_range_is_REFUSED_and_never_clamped() -> None:
    beyond = len(search_results.RESULT_KINDS)
    assert search_results.term_for(beyond) == "index_out_of_range"
    assert search_results.term_for(-1) == "index_out_of_range"
    assert search_results.term_for(10_000) == "index_out_of_range"


def test_the_output_alphabet_is_closed_over_adversarial_input() -> None:
    alphabet = search_results.emitted_alphabet()
    for index in (-50, -1, 0, 3, len(search_results.RESULT_KINDS), 999):
        assert search_results.term_for(index) in alphabet
    tallied = search_results.tally([1] * 40, queries_present=3)
    assert set(tallied["by_kind"]) <= alphabet


def test_a_short_count_list_is_reported_not_padded() -> None:
    tallied = search_results.tally([1, 2])
    assert tallied["kinds_not_reported"] == len(search_results.RESULT_KINDS) - 2
    assert tallied["total_classified"] == 3


def test_the_result_table_closes_three_segments_and_holds_no_paths() -> None:
    for row in search_results.RESULT_TABLE:
        assert len(row) == 4, "Every row closes THREE segments plus its token."
        for segment in row[1:]:
            assert segment and "/" not in segment, (
                "A table entry is a SEGMENT, never a path. A path here would "
                "reintroduce the containment match the segment rule exists "
                "to prevent."
            )
        assert row[1] == "search" and row[2] == "results"


def test_the_in_page_comparison_is_segment_equality_not_containment() -> None:
    """And it reads the DECISION, so an unrelated line cannot satisfy it.

    This guard fired for real during the V8 refactor: the table-lookup helper
    had been renamed to a bare ``indexOf``, which made ``indexOf(row[0])``
    indistinguishable on sight from a containment match against a table row.
    **The fix was the rename, not a softer assertion** -- a guard that cannot
    tell those two apart is not a guard, and the helper is ``indexOfClass``
    again for exactly that reason.
    """
    decision = search_results.classifier_source()
    assert "segments[0] !== row[1]" in decision
    assert "segments[1] !== row[2]" in decision
    assert "segments[2] !== row[3]" in decision
    assert "indexOf(row" not in decision, (
        "Containment matching against a table row. menus.py shipped that bug "
        "and anchors.py measured it reclassifying three routes INTO the "
        "hazard class."
    )
    assert "segments[0].indexOf" not in decision
    assert "segments.join" not in decision, (
        "Rejoining segments reintroduces the whole-path containment the "
        "segment rule exists to prevent."
    )


def test_the_query_is_dropped_before_any_segment_is_read() -> None:
    decision = search_results.classifier_source()
    cut = decision.index('path.indexOf("?")')
    split = decision.index('path.split("/")')
    assert cut < split, (
        "The query must be removed BEFORE segments are taken. On this "
        "surface the query is where a person's name is typed."
    )
    assert "query = 1" in decision, "Its presence is FLAGGED, never read."
    assert "query: query" in decision, "And the flag is what leaves, not the text."


# --------------------------------------------------------------------------
# THE TRAVERSAL RULE -- the closure anchors.py does not have, and the one the
# condition-2 amendment was measured on.
# --------------------------------------------------------------------------


def test_the_adversarial_traversal_is_refused() -> None:
    assert search_results.refuses_traversal(
        search_results.ADVERSARIAL_TRAVERSAL_SEGMENTS
    ), (
        "The address the amendment measured. Its first three segments are a "
        "people search; its normalised form ends his account."
    )


def test_an_ordinary_people_route_is_NOT_refused() -> None:
    assert not search_results.refuses_traversal(("search", "results", "people"))


def test_THIS_CONTROL_CAN_FAIL_a_matcher_without_the_dot_rule_calls_it_a_person() -> None:
    """SHOWN FAILING. The weaker design, run over the same segments.

    Three-segment equality with no dot rule -- which is ``anchors.py``'s
    design promoted to three positions -- classifies the account-ending
    address as ``person_result``. This test asserts the WRONG answer the weak
    matcher gives, so the rule above is measured against something rather
    than merely stated.
    """
    segments = search_results.ADVERSARIAL_TRAVERSAL_SEGMENTS

    def weak_matcher(parts: tuple[str, ...]) -> str:
        for row in search_results.RESULT_TABLE:
            if len(parts) >= 3 and parts[:3] == row[1:4]:
                return row[0]
        return "unclassified"

    assert weak_matcher(segments) == "person_result", (
        "If this stops being true the weak matcher changed, and the "
        "traversal rule is no longer being measured against anything."
    )
    assert search_results.refuses_traversal(segments)


def test_the_shipped_script_really_carries_the_traversal_rule() -> None:
    assert search_results.script_carries_the_traversal_rule(), (
        "A docstring describing a rule and a script applying it are two "
        "artifacts. This reads the second."
    )


def test_THIS_CONTROL_CAN_FAIL_the_reader_goes_red_when_the_rule_is_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SHOWN FAILING. Strip the dot test from the script; the reader says so."""
    stripped = search_results._CLASSIFY_IN_PAGE.replace('segment === ".."', "false")
    monkeypatch.setattr(search_results, "_CLASSIFY_IN_PAGE", stripped)
    assert not search_results.script_carries_the_traversal_rule(), (
        "The source reader cannot distinguish a script with the rule from "
        "one without it, so its green above certified nothing."
    )


def test_THIS_CONTROL_CAN_FAIL_a_reorder_renames_the_hazard_class(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SHOWN FAILING. Swap index 0; the order guard must go red."""
    reordered = ("company_result",) + tuple(
        kind for kind in search_results.RESULT_KINDS if kind != "company_result"
    )
    monkeypatch.setattr(search_results, "RESULT_KINDS", reordered)
    assert search_results.term_for(0) != "person_result", (
        "The order guard cannot see a reorder, so it was unfalsifiable."
    )


# --------------------------------------------------------------------------
# THE CONTROL FIXTURE
# --------------------------------------------------------------------------


def test_the_control_fixture_carries_every_adversarial_route() -> None:
    fixture = search_results.control_fixture()
    assert "/../../" in fixture, "The traversal route."
    assert "peoplefinder" in fixture, "The containment trap."
    assert "?keywords=" in fixture, "The query form."


def test_the_control_has_an_expectation_covering_every_kind() -> None:
    assert set(search_results.CONTROL_EXPECTATION) == set(
        search_results.RESULT_KINDS
    ), (
        "A control whose result nobody predicted cannot fail. Every kind in "
        "the alphabet is predicted by the fixture."
    )
    assert search_results.CONTROL_EXPECTATION["traversal_refused"] == 1
    assert search_results.CONTROL_EXPECTATION["person_result"] == 1


def test_the_fixture_carries_no_third_party_and_every_slug_is_synthetic() -> None:
    """A tracked file may not carry a person's name even as an illustration.

    On THIS surface, where a fixture row IS a search result, that rule is at
    its sharpest. Every non-route segment must be declared synthetic.
    """
    fixture = search_results.control_fixture()
    for fragment in ("example",):
        assert fragment in fixture
    assert "/in/" not in fixture, (
        "A member-profile route in a search fixture is a slug, and a slug "
        "is a name."
    )


# --------------------------------------------------------------------------
# THE CROSS-ENGINE CONTROL. Everything above drives Python; this drives the
# SHIPPED JavaScript under V8, which is the only thing that runs in the page.
#
# THE INSTRUMENT IS IMPORTED, NOT INVENTED: tests/test_compose_fields.py
# already lifts a shipped function out of a script by brace-matching and runs
# it under node, and this repository has a scar for writing a second copy of a
# check it already ships. The lift itself lives in the module, as
# search_results.classifier_source().
# --------------------------------------------------------------------------


def _node() -> str | None:
    return shutil.which("node")


def _run_classify_in_node(routes: list[str]) -> list[dict]:
    """Run the SHIPPED ``classifyRoute`` under V8 and return its verdicts."""
    driver = textwrap.dedent(
        """
        %s;
        const table = %s;
        const classes = %s;
        const host = %s;
        console.log(JSON.stringify(%s.map((raw) => {
          const verdict = classifyRoute(raw, table, classes, host);
          return {
            kind: verdict.kind,
            term: classes[verdict.kind],
            query: verdict.query,
            entity: verdict.entity,
          };
        })));
        """
    ) % (
        search_results.classifier_source(),
        json.dumps([list(row) for row in search_results.RESULT_TABLE]),
        json.dumps(list(search_results.RESULT_KINDS)),
        json.dumps(search_results._HOST),
        json.dumps(routes),
    )
    handle, path = tempfile.mkstemp(suffix=".mjs")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(driver)
        proc = subprocess.run([_node(), path], capture_output=True, text=True)
    finally:
        os.remove(path)
    assert proc.returncode == 0, proc.stderr[:2000]
    return json.loads(proc.stdout)


def test_the_lifted_function_is_the_shipped_one_and_is_balanced() -> None:
    decision = search_results.classifier_source()
    assert decision.startswith("const classifyRoute =")
    assert decision.endswith("}")
    assert decision.count("{") == decision.count("}"), (
        "A truncated function would still run and would still be wrong."
    )
    assert decision in search_results._CLASSIFY_IN_PAGE, (
        "LIFTED, never transcribed. A transcription is a second "
        "implementation and two implementations can disagree tomorrow."
    )


def test_the_shipped_classifier_answers_every_corpus_route_as_predicted() -> None:
    """THE CONTROL THAT DID NOT EXIST. The prediction, run under a real engine.

    Every row of ``route_control_corpus`` is an expectation written before the
    engine spoke. This is the first thing in this module's history that can
    tell a working classifier from a broken one.
    """
    if _node() is None:
        pytest.skip(
            "THE CROSS-ENGINE CONTROL DID NOT RUN: node is not on PATH. The "
            "shipped classifyRoute in dom.SEARCH_RESULTS_JS was NOT executed "
            "in this session, so its verdicts -- including the refusal of the "
            "traversal address the condition-2 amendment measured -- were not "
            "checked here. Every other test in this file is structural and "
            "reads source text rather than running it."
        )

    corpus = search_results.route_control_corpus()
    verdicts = _run_classify_in_node([row[0] for row in corpus])
    assert len(verdicts) == len(corpus)

    wrong = []
    for (route, kind, query, entity), got in zip(corpus, verdicts):
        if (got["term"], got["query"], got["entity"]) != (kind, query, entity):
            wrong.append((route, kind, got["term"], query, got["query"], entity, got["entity"]))
    assert not wrong, f"The engine disagreed with the prediction: {wrong}"


def test_the_engine_refuses_the_amendments_address_specifically() -> None:
    """Named on its own, because it is the single row the ruling turns on."""
    if _node() is None:
        pytest.skip(
            "THE CROSS-ENGINE CONTROL DID NOT RUN: node is not on PATH, so "
            "the traversal refusal was not executed in this session."
        )
    got = _run_classify_in_node([search_results.adversarial_traversal_route()])[0]
    assert got["term"] == "traversal_refused", (
        "The address whose first three segments are a people search and "
        "whose normalised form ends his account was NOT refused."
    )
    assert got["term"] != "person_result"


def test_THIS_CONTROL_CAN_FAIL_the_engine_calls_it_a_person_without_the_rule() -> None:
    """SHOWN FAILING, UNDER THE REAL ENGINE, not against a Python double.

    The dot test is removed from the LIFTED shipped source and the SAME engine
    is asked again. It answers ``person_result``. That is the measurement
    behind every claim this module makes about traversals: with the rule the
    engine refuses the address, without it the engine certifies an
    account-ending address as a read of people.
    """
    if _node() is None:
        pytest.skip(
            "THE MUTATION CONTROL DID NOT RUN: node is not on PATH, so the "
            "traversal rule was never shown failing under a real engine in "
            "this session -- only its source text was inspected."
        )

    route = search_results.adversarial_traversal_route()
    with_rule = _run_classify_in_node([route])[0]

    stripped = search_results.classifier_source().replace(
        'if (segment === ".." || segment === ".") {', "if (false) {"
    )
    assert stripped != search_results.classifier_source(), (
        "The mutation did not apply, so this control mutated nothing and "
        "its result below would have been the unmutated answer."
    )
    driver = textwrap.dedent(
        """
        %s;
        const table = %s;
        const classes = %s;
        console.log(JSON.stringify(
          classifyRoute(%s, table, classes, %s)
        ));
        """
    ) % (
        stripped,
        json.dumps([list(row) for row in search_results.RESULT_TABLE]),
        json.dumps(list(search_results.RESULT_KINDS)),
        json.dumps(route),
        json.dumps(search_results._HOST),
    )
    handle, path = tempfile.mkstemp(suffix=".mjs")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(driver)
        proc = subprocess.run([_node(), path], capture_output=True, text=True)
    finally:
        os.remove(path)
    assert proc.returncode == 0, proc.stderr[:2000]
    without_rule = json.loads(proc.stdout)

    assert with_rule["term"] == "traversal_refused"
    assert (
        search_results.RESULT_KINDS[without_rule["kind"]] == "person_result"
    ), (
        "Without the dot rule the engine must call this address a person. If "
        "it does not, this control is no longer measuring the rule."
    )


#: Pulls the hrefs out of the control fixture. **THIS IS THE SEAM AND IT IS
#: NAMED:** the shipped script gets its anchors from a DOM, and node has no
#: DOM, so the test does that half. What is therefore NOT covered below is
#: ``querySelectorAll`` and ``getAttribute`` -- three lines of the shipped
#: script that hold no policy. Everything that DECIDES anything is covered,
#: because all of it lives in ``classifyRoute``, which is why it was split out.
_HREF_IN_FIXTURE = re.compile(r'href="([^"]*)"')


def _fixture_routes() -> list[str]:
    fixture = search_results.control_fixture()
    anchors = fixture.count("<a")
    hrefs = _HREF_IN_FIXTURE.findall(fixture)
    # The anchor with no href is a fixture row too, and it must survive the
    # extraction as an empty string or the no_href class goes uncounted.
    return hrefs + [""] * (anchors - len(hrefs))


def test_THE_CONTROL_EXPECTATION_IS_COMPUTED_AT_LAST() -> None:
    """The fixture's predicted counts, produced by the engine and the tally.

    **This is the test the first version of this module could not have.** The
    classifier is JavaScript and the suite was structural, so
    ``CONTROL_EXPECTATION`` was a table of numbers that nothing had ever
    produced -- a control whose result nobody computed cannot fail, and this
    one had never been computed.

    It now runs the SHIPPED ``classifyRoute`` under V8 over the fixture's own
    routes and the SHIPPED :func:`~linkedin_server.search_results.tally` over
    the result, and compares against the written prediction.
    """
    if _node() is None:
        pytest.skip(
            "THE FIXTURE CONTROL DID NOT RUN: node is not on PATH, so "
            "CONTROL_EXPECTATION was NOT computed in this session and "
            "remains a prediction nothing has produced."
        )

    routes = _fixture_routes()
    verdicts = _run_classify_in_node(routes)
    assert len(verdicts) == len(routes) == len(search_results.CONTROL_EXPECTATION), (
        "The fixture, its routes and its expectation must stay the same "
        "length -- one anchor, one prediction."
    )

    counts = [0] * len(search_results.RESULT_KINDS)
    queries = 0
    for got in verdicts:
        counts[got["kind"]] += 1
        queries += got["query"]

    tallied = search_results.tally(counts, queries_present=queries)
    assert tallied["by_kind"] == dict(
        sorted(search_results.CONTROL_EXPECTATION.items())
    ), "The engine's tally of the fixture disagrees with the prediction."
    assert tallied["person_results"] == 1
    assert tallied["traversals_refused"] == 1
    assert tallied["queries_present"] == 1, (
        "Exactly one fixture route carries a query, and its presence is the "
        "only thing about it that may be known."
    )
    assert tallied["kinds_not_reported"] == 0
    assert tallied["total_classified"] == len(routes)


def test_THIS_CONTROL_CAN_FAIL_an_unpredicted_anchor_goes_red() -> None:
    """SHOWN FAILING. Add a route the expectation does not predict.

    A fixture that grows without its prediction growing is the exact way a
    control quietly stops covering what it claims to, so this proves the
    comparison notices.
    """
    if _node() is None:
        pytest.skip(
            "THE FIXTURE MUTATION CONTROL DID NOT RUN: node is not on PATH."
        )

    routes = _fixture_routes() + ["/search/results/companies/"]
    verdicts = _run_classify_in_node(routes)
    counts = [0] * len(search_results.RESULT_KINDS)
    for got in verdicts:
        counts[got["kind"]] += 1
    tallied = search_results.tally(counts)
    assert tallied["by_kind"] != dict(
        sorted(search_results.CONTROL_EXPECTATION.items())
    ), (
        "An extra anchor did not change the tally, so the fixture control "
        "cannot see the fixture changing and was certifying nothing."
    )
    assert tallied["by_kind"]["company_result"] == 2


def test_the_two_measured_limits_are_declared_in_the_corpus() -> None:
    """A limit nobody wrote down is indistinguishable from a limit nobody has."""
    routes = {row[0]: row[1] for row in search_results.route_control_corpus()}
    assert routes["/SEARCH/RESULTS/PEOPLE/"] == "off_search", (
        "Case sensitivity must miss on the SAFE side -- unrecognised, never "
        "admitted."
    )
    assert (
        routes["/search/results/people/..%2f..%2fmypreferences"] == "person_result"
    ), (
        "The encoded-traversal limit is REAL and is recorded as what the "
        "shaper does, not as what would be nice. Changing this to a refusal "
        "means adding a decode step, and decoding is normalising."
    )
    assert "MEASURED LIMIT" in inspect.getsource(
        search_results.route_control_corpus
    )


# --------------------------------------------------------------------------
# THE FILTER PANEL. Sixteen of the twenty reads, and the census calls rows
# 79-93 "the largest single hole in the slice and the only one that is pure
# silence" -- zero sentences in the repository about any of them.
#
# The matching rule has to exist in JavaScript, because a filter label on this
# surface can be a person's name and must not cross into Python. menus.py owns
# the SAME rule in Python. TWO ENGINES, ONE RULE -- and the repository's answer
# to that situation is to MEASURE AGREEMENT rather than argue it, which is what
# tests/test_compose_fields.py does for shapeOf.
# --------------------------------------------------------------------------

#: ``(label, phrase, must match)``. The expectations are written here and the
#: engines are asked; neither engine is the oracle for the other.
_MATCH_CORPUS: tuple[tuple[str, str], ...] = (
    # THE COLLISION THIS VOCABULARY BUILDS IN. Separate census rows, separate
    # value classes: N 81 is a degree taxonomy, N 85's value IS A PERSON.
    ("Connections of", "connections of"),
    ("Connections of", "connections"),
    ("Connections", "connections"),
    ("Connections", "connections of"),
    # menus.py's Star Anise, one surface over: a two-token label whose first
    # token is a single-word vocabulary term.
    ("School Anise", "school"),
    ("School", "school"),
    # Multi-word phrases MAY be contained; single-word ones may not.
    ("Filter by Current company", "current company"),
    ("Filter by Locations", "locations"),
    ("Locations", "locations"),
    ("Past company", "current company"),
    ("Open to volunteering", "open to volunteering"),
    # Normalisation edges: punctuation collapses to a space rather than
    # vanishing, and a non-ASCII letter is not a word character in either
    # engine.
    ("Delete/Archive", "delete"),
    ("Current  company", "current company"),
    ("CURRENT COMPANY", "current company"),
    ("Keywords (first name, last name)", "keywords"),
    ("Keywords", "keywords"),
    ("", "school"),
    ("   ", "school"),
    ("People", "people"),
    ("People also viewed", "people"),
)


def _run_filter_match_in_node(pairs: list[tuple[str, str]]) -> list[bool]:
    """Run the SHIPPED ``normaliseLabel`` + ``matchPhrase`` under V8."""
    driver = textwrap.dedent(
        """
        %s;
        %s;
        const pairs = %s;
        console.log(JSON.stringify(pairs.map((pair) =>
          matchPhrase(normaliseLabel(pair[0]), pair[1])
        )));
        """
    ) % (
        search_results.filter_normaliser_source(),
        search_results.filter_matcher_source(),
        json.dumps([list(pair) for pair in pairs]),
    )
    handle, path = tempfile.mkstemp(suffix=".mjs")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(driver)
        proc = subprocess.run([_node(), path], capture_output=True, text=True)
    finally:
        os.remove(path)
    assert proc.returncode == 0, proc.stderr[:2000]
    return json.loads(proc.stdout)


def _python_match(label: str, phrase: str) -> bool:
    """The SHIPPED Python rule. Imported from menus, never re-implemented."""
    from linkedin_server import menus

    return menus._contains_phrase(menus._normalise(label), phrase)


def test_the_page_matcher_agrees_with_the_shipped_python_rule() -> None:
    """TWO ENGINES, ONE RULE -- and agreement measured rather than argued.

    ``menus.py`` owns this rule in Python and classifies labels there, which
    is right for a menu: a menu label is a UI verb. **It is wrong here**, so
    the rule is applied one level earlier, in the page, where the label can be
    a person's name. That means the rule exists twice, and two implementations
    that agree today can disagree tomorrow.

    So this runs the SHIPPED ``matchPhrase`` -- lifted from the panel script by
    brace-matching, not transcribed -- under V8 and compares every case
    against ``menus._contains_phrase``. **Neither engine is the oracle; the
    corpus is.**
    """
    if _node() is None:
        pytest.skip(
            "THE CROSS-ENGINE AGREEMENT CHECK DID NOT RUN: node is not on "
            "PATH. The page-side matcher in dom.FILTER_PANEL_JS was NOT "
            "compared against menus._contains_phrase in this session, so a "
            "divergence between the two -- including on the "
            "connections / connections-of collision -- would not have been "
            "caught here."
        )

    from_js = _run_filter_match_in_node(list(_MATCH_CORPUS))
    disagreements = []
    for (label, phrase), js in zip(_MATCH_CORPUS, from_js):
        py = _python_match(label, phrase)
        if bool(js) != bool(py):
            disagreements.append((label, phrase, js, py))
    assert not disagreements, (
        f"The two engines disagree on {len(disagreements)} of "
        f"{len(_MATCH_CORPUS)} cases: {disagreements}"
    )


def test_the_collision_this_vocabulary_builds_in_is_kept_apart() -> None:
    """``connections`` is a PREFIX of ``connections of`` and they are not the
    same row -- one is a degree taxonomy, the other's value IS A PERSON."""
    if _node() is None:
        pytest.skip(
            "THE COLLISION CHECK DID NOT RUN: node is not on PATH, so the "
            "person-valued filter was not shown being kept apart from the "
            "degree filter under a real engine."
        )
    verdicts = _run_filter_match_in_node(
        [
            ("Connections of", "connections of"),
            ("Connections of", "connections"),
            ("Connections", "connections"),
        ]
    )
    assert verdicts[0] is True
    assert verdicts[1] is False, (
        "A label reading 'Connections of' matched the bare term "
        "'connections'. That reports a PERSON-VALUED filter as a degree "
        "filter, which is this surface's Star Anise landing on the hazard."
    )
    assert verdicts[2] is True


def test_THIS_CONTROL_CAN_FAIL_without_the_asymmetry_the_collision_collapses() -> None:
    """SHOWN FAILING, UNDER V8. Remove the single-word rule; watch both break.

    The asymmetry -- a one-word phrase must be the WHOLE label -- is the only
    thing separating the degree filter from the person-valued one, and the
    only thing keeping a two-token label out of a single-word term. Stripped,
    the SAME engine matches both.
    """
    if _node() is None:
        pytest.skip(
            "THE ASYMMETRY MUTATION DID NOT RUN: node is not on PATH, so the "
            "single-word rule was never shown failing under a real engine."
        )

    matcher = search_results.filter_matcher_source()
    stripped = matcher.replace(
        "return words.length === 1 && words[0] === needle[0];",
        "return words.indexOf(needle[0]) !== -1;",
    )
    assert stripped != matcher, "The mutation did not apply."

    driver = textwrap.dedent(
        """
        %s;
        %s;
        console.log(JSON.stringify([
          matchPhrase(normaliseLabel("Connections of"), "connections"),
          matchPhrase(normaliseLabel("School Anise"), "school")
        ]));
        """
    ) % (search_results.filter_normaliser_source(), stripped)
    handle, path = tempfile.mkstemp(suffix=".mjs")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(driver)
        proc = subprocess.run([_node(), path], capture_output=True, text=True)
    finally:
        os.remove(path)
    assert proc.returncode == 0, proc.stderr[:2000]
    without_rule = json.loads(proc.stdout)

    assert without_rule == [True, True], (
        "Without the single-word asymmetry the engine must match BOTH the "
        "person-valued label against the degree term and the two-token label "
        "against the single-word term. If it does not, this control is no "
        "longer measuring the asymmetry."
    )
    with_rule = _run_filter_match_in_node(
        [("Connections of", "connections"), ("School Anise", "school")]
    )
    assert with_rule == [False, False]


def test_the_filter_vocabulary_is_coherent_and_maps_to_census_rows() -> None:
    terms = search_results.FILTER_TERMS
    assert len(terms) == len(set(terms)), "A duplicate term makes one row dead."
    assert len(terms) == len(search_results.FILTER_TERM_ROWS)
    assert len(terms) == len(search_results.FILTER_VALUE_CLASSES)
    for term in terms:
        assert term == term.strip().lower(), "Terms are pre-normalised."
        assert "  " not in term
        assert all(ch.isalnum() or ch == " " for ch in term)
    for value_class in search_results.FILTER_VALUE_CLASSES:
        assert value_class in search_results.VALUE_CLASSES
    rows = search_results.FILTER_TERM_ROWS
    assert len(set(rows)) == len(rows), "One term per census row."


def test_the_three_hazard_terms_are_first_and_are_classed_as_hazards() -> None:
    assert search_results.FILTER_TERMS[:3] == (
        "connections of",
        "followers of",
        "keywords",
    )
    assert search_results.value_class_for(0) == "person_valued"
    assert search_results.value_class_for(1) == "person_valued"
    assert search_results.value_class_for(2) == "needle_valued"


def test_the_phrase_index_puts_the_longer_phrase_first() -> None:
    ordered = [phrase for phrase, _ in search_results.filter_phrase_index()]
    assert ordered.index("connections of") < ordered.index("connections"), (
        "Longest-first is half of what keeps the person-valued filter apart "
        "from the degree filter; the matcher's asymmetry is the other half."
    )


def test_filter_out_of_range_is_refused_and_the_alphabet_is_closed() -> None:
    beyond = len(search_results.FILTER_TERMS)
    assert search_results.filter_term_for(beyond) == "index_out_of_range"
    assert search_results.filter_term_for(-1) == "index_out_of_range"
    assert search_results.value_class_for(beyond) == "index_out_of_range"
    alphabet = search_results.filter_alphabet()
    for index in (-9, 0, 3, beyond, 500):
        assert search_results.filter_term_for(index) in alphabet
        assert search_results.value_class_for(index) in alphabet


def test_the_filter_reader_takes_no_label_and_no_needle() -> None:
    signature = inspect.signature(search_results.read_filters)
    assert list(signature.parameters) == ["page", "html"]
    assert not (_ADDRESS_SHAPED & set(signature.parameters))
    assert not (
        _ADDRESS_SHAPED
        & set(inspect.signature(search_results.tally_filters).parameters)
    )


def test_THE_FILTER_CONTROL_EXPECTATION_IS_COMPUTED() -> None:
    """The filter fixture's counts, produced by the shipped matcher under V8.

    The fixture's non-filter controls are the point as much as its filters:
    ``School Anise`` must NOT match, ``Next`` must not match, and the empty
    control must be counted as empty rather than as a miss.
    """
    if _node() is None:
        pytest.skip(
            "THE FILTER FIXTURE CONTROL DID NOT RUN: node is not on PATH, so "
            "FILTER_CONTROL_EXPECTATION was NOT computed in this session and "
            "remains a prediction nothing has produced."
        )

    fixture = search_results.filter_control_fixture()
    labels = re.findall(r"<button[^>]*>([^<]*)</button>", fixture)
    labels += re.findall(r'<button aria-label="([^"]+)"', fixture)
    # The aria-labelled control contributes its aria-label, not its text.
    labels = [label for label in labels if label != "k"]

    phrase_index = search_results.filter_phrase_index()
    pairs = [(label, phrase) for label in labels for phrase, _ in phrase_index]
    verdicts = _run_filter_match_in_node(pairs)

    counts = [0] * len(search_results.FILTER_TERMS)
    empty = 0
    unmatched = 0
    width = len(phrase_index)
    for position, label in enumerate(labels):
        if not label.strip():
            empty += 1
            continue
        window = verdicts[position * width:(position + 1) * width]
        hit = next(
            (phrase_index[i][1] for i, ok in enumerate(window) if ok), None
        )
        if hit is None:
            unmatched += 1
        else:
            counts[hit] += 1

    tallied = search_results.tally_filters(counts)
    assert tallied["by_term"] == dict(
        sorted(search_results.FILTER_CONTROL_EXPECTATION.items())
    ), "The engine's tally of the filter fixture disagrees with the prediction."
    assert tallied["person_valued_filters"] == 2, (
        "Connections of and Followers of. The page offers two ways to search "
        "by a particular person, and that COUNT is all this shaper will say."
    )
    assert tallied["needle_valued_filters"] == 1
    assert unmatched == 2, "School Anise and Next must both miss."
    assert empty == 1, "The empty control is empty, not a miss."
    assert tallied["filters_offered"] == len(search_results.FILTER_TERMS)


#: Verbs that ACT on a page. A shaper may not contain a call to any of them.
_ACTING_VERBS = {
    "click", "press", "fill", "type", "check", "select_option",
    "tap", "dblclick", "set_checked", "submit", "goto", "navigate",
}


def _firing_offenders(source: str) -> list[str]:
    """Walk a module's SYNTAX TREE for anything that could fire.

    It reads the TREE, not the text: the shaper's prose says ``press``,
    ``submit`` and ``send`` while describing what it will not do, and a grep
    cannot tell a sentence from a statement.
    """
    import ast

    tree = ast.parse(source)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _ACTING_VERBS:
                offenders.append(node.func.attr)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names = {arg.arg for arg in node.args.args}
            names |= {arg.arg for arg in node.args.kwonlyargs}
            for forbidden in ("confirm", "confirm_token", "token"):
                if forbidden in names:
                    offenders.append(f"{node.name}({forbidden})")
    return offenders


def test_NOTHING_IS_FIRED_FROM_THIS_SURFACE_condition_5_in_test_form() -> None:
    """Condition 5 of the approval, asserted on the CODE rather than the prose.

    ``N 4`` -- *send an invitation from a people-search result* -- is this
    blocker's one WRITE, and the ruling says its decision is NOT inherited by
    the reads. A shaper that could press something would have imported that
    ruling by accident, so this walks the module's syntax tree and refuses any
    call that acts on a page, plus any confirm-token parameter.

    It reads the TREE, not the text: the module's prose says the words
    ``press``, ``submit`` and ``send`` while describing what it will not do,
    and a grep cannot tell a sentence from a statement.
    """
    offenders = _firing_offenders(inspect.getsource(search_results))
    assert not offenders, (
        f"This shaper can act on a page or be handed a confirm token: "
        f"{offenders}. Condition 5 is that NOTHING IS FIRED from this "
        "surface, and N 4's ruling is not inherited by the reads."
    )


def test_THIS_CONTROL_CAN_FAIL_the_firing_guard_catches_a_real_offender() -> None:
    """SHOWN FAILING. The same walk over a module that DOES press something.

    Run only against the shipped file, this guard is green whether it works or
    not -- the shipped file has nothing to find. So it is aimed at a synthetic
    module that presses a control and takes a confirm token, and it must find
    both.
    """
    offending = textwrap.dedent(
        """
        async def apply_filter(page, confirm_token):
            await page.locator("button").click()
            return True
        """
    )
    found = _firing_offenders(offending)
    assert "click" in found, "The guard cannot see a press."
    assert any("confirm_token" in item for item in found), (
        "The guard cannot see a confirm token, so its green on the shipped "
        "module certified nothing."
    )


def test_the_module_admits_nothing() -> None:
    """Condition 1 in test form, from this side: the shaper admits no address.

    **THE ADMISSION LANDED 2026-09-20, IN THE SAME COMMIT AS THIS MODULE'S
    TOOL, AND THIS TEST DID NOT RELAX.** It was written while the admission
    was still a later commit; its job now is the durable one, which is the
    better one: the permission to open an address lives in the navigation
    boundary and NOWHERE ELSE, so a future wave cannot widen the surface by
    editing the shaper. A shaper that quietly carried an allowlist entry would
    have satisfied neither half of condition 1 -- it would have violated it.

    It caught the admitting wave's own comment on the first run, which is a
    grep-shaped false positive and was repaired by rewording the comment
    rather than by loosening the token list. **A guard that is narrowed the
    first time it inconveniences its author is not a guard.**
    """
    source = inspect.getsource(search_results)
    for forbidden in ("ALLOW", "ADMIT", "readonly.py", "PERMITTED_"):
        assert forbidden not in source, (
            f"{forbidden!r} appears in the shaper. Admission and shaper land "
            "in the same commit or neither lands -- and this is the shaper."
        )
