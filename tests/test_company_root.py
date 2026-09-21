"""The count reader reads ELEVEN where the screen-reader copy says forty-one.

``linkedin_server/company_root.py`` opens an organisation Page root -- an
address admitted on 2026-09-20 that nothing in this package navigated to -- and
reduces it to integers. The page is third-party dense: the allowlist entry's
own warning is that the root draws *"a module naming employees the operator
knows"*, so the line this reader is aimed at is the most likely place on the
page for somebody's name to sit.

## THE HEADLINE CONTROL, AND IT RUNS THE SHIPPED SCRIPT

``dom.COUNT_LINES_JS`` is the only thing that runs in the page, so a Python
re-implementation of its rules would be a second, disagreeing copy -- the scar
``search_results.py`` records for exactly this. This file therefore runs **the
shipped script itself, under V8**, over a synthetic node tree built from
``company_root.control_tree()``. Node has no DOM, so the tree is supplied
rather than parsed; the SCRIPT is not touched.

**AND IT IS SHOWN FAILING ON A PLANTED DEFECT.** The one line that steps over
a screen-reader subtree is replaced with a line that steps over nothing, and
the same fixture is re-driven. The shipped script reads ELEVEN. The defective
one reads FORTY-ONE -- the number out of the accessible copy. That is the
hazard measured on the search card arriving on this surface, and the skip is
what stops it.

**WHAT THE DEFECT DOES NOT DO IS LEAK**, and saying so is the honest half: the
plant does not reach the output in either build, because the return value is
integers by construction. The exclusion buys a CORRECT NUMBER here; the
name-freedom is bought one layer down and does not depend on it.
"""

from __future__ import annotations

import inspect
import json
import os
import shutil
import subprocess
import tempfile

import pytest

from linkedin_server import coerce, company_page, company_root, dom, readonly
from tests.plantedpage import PLANT, PlantedPage, carries_the_plant

IDENTIFIER = "5417062"

#: A synthetic slug that is person-SHAPED. A sole trader, an eponymous firm or
#: a personal brand gets a person's name in its slug, and this repository's own
#: corpus carries one.
EPONYMOUS_SLUG = "exampleone-markersurname-associates"


# ---------------------------------------------------------------------------
# 1. The constants are the contract
# ---------------------------------------------------------------------------


def test_every_shipped_phrase_is_already_in_the_form_the_page_compares():
    """The phrase table crosses into the page verbatim.

    ``normalised`` is NOT a second matcher -- nothing calls it on page text.
    It exists so this static property of a constant is checked once, rather
    than a transform running at read time that could drift from the one in
    the document.
    """
    for kind, phrase in company_root.COUNT_PHRASES:
        assert kind in company_root.COUNT_KINDS, kind
        assert company_root.normalised(phrase) == phrase, phrase
        assert phrase == phrase.strip()


def test_no_shipped_phrase_contains_another():
    """Two phrases where one contains the other read one number twice.

    That would arrive as corroboration and is a single observation, and on the
    disagreement branch it would be worse: one line would argue with itself.
    """
    shipped = company_root.phrases_shipped()
    for first in shipped:
        for second in shipped:
            if first == second:
                continue
            assert f" {first} " not in f" {second} ", (first, second)


def test_the_substitution_default_lands_on_a_class_that_publishes_no_number():
    """INDEX 0 IS WHERE GARBAGE LANDS, so index 0 must be harmless.

    ``coerce`` substitutes a refused value with ``0`` and counts it. An
    alphabet with ``plain_digits`` first would turn a value the page refused
    into "trust this number", which is the flattering direction and the one
    nobody would have looked at.
    """
    assert company_root.NUMERAL_SHAPES[0] == "no_digit_run"
    verdict = company_root.connection_counts(
        {
            "elements": 40,
            "chunks": 9,
            "matches": [{"phrase": 0, "shape": 0, "value": 99, "chars": 12}],
        }
    )["by_kind"]["connections_at_organisation"]
    assert verdict["state"] == "numeral_refused"
    assert verdict["value"] is None


def test_position_lookups_refuse_out_of_range_rather_than_clamping():
    assert company_root.kind_for(0) == "connections_at_organisation"
    assert company_root.kind_for(-1) == "position_out_of_range"
    assert company_root.kind_for(len(company_root.COUNT_PHRASES)) == (
        "position_out_of_range"
    )
    assert company_root.term_for(len(company_root.NUMERAL_SHAPES)) == (
        "position_out_of_range"
    )


# ---------------------------------------------------------------------------
# 2. A missing phrase is never a zero
# ---------------------------------------------------------------------------


def test_a_phrase_that_did_not_render_is_not_reported_as_a_count_of_zero():
    """The whole honesty of an unmeasured vocabulary rests on this branch."""
    out = company_root.connection_counts(
        {"elements": 900, "chunks": 300, "matches": []}
    )["by_kind"]["connections_at_organisation"]
    assert out["state"] == "phrase_not_drawn"
    assert out["value"] is None
    assert "NOT A COUNT OF ZERO" in out["why"]


def test_a_page_that_drew_no_element_is_a_fact_about_the_reader():
    out = company_root.connection_counts(
        {"elements": 0, "chunks": 0, "matches": []}
    )["by_kind"]["connections_following_page"]
    assert out["state"] == "reader_blind"
    assert out["value"] is None
    assert "READER" in out["why"]


def test_an_abbreviation_is_refused_and_never_rounded():
    out = company_root.connection_counts(
        {
            "elements": 40,
            "chunks": 9,
            "matches": [{"phrase": 0, "shape": 3, "value": 0, "chars": 12}],
        }
    )["by_kind"]["connections_at_organisation"]
    assert out["state"] == "numeral_refused"
    assert out["numeral"] == "abbreviated_refused"
    assert out["value"] is None


def test_two_phrases_disagreeing_withhold_both_rather_than_choosing():
    """Choosing would be this reader preferring one of LinkedIn's own lines."""
    out = company_root.connection_counts(
        {
            "elements": 40,
            "chunks": 9,
            "matches": [
                {"phrase": 0, "shape": 1, "value": 11, "chars": 24},
                {"phrase": 2, "shape": 1, "value": 12, "chars": 30},
            ],
        }
    )["by_kind"]["connections_at_organisation"]
    assert out["state"] == "disagreement"
    assert out["value"] is None


def test_a_refused_numeral_does_not_poison_a_good_reading_of_the_same_kind():
    """One unusable line among two is one unusable line, not a lost reading."""
    out = company_root.connection_counts(
        {
            "elements": 40,
            "chunks": 9,
            "matches": [
                {"phrase": 3, "shape": 2, "value": 1204, "chars": 34},
                {"phrase": 5, "shape": 3, "value": 0, "chars": 34},
            ],
        }
    )["by_kind"]["connections_following_page"]
    assert out["state"] == "count_read"
    assert out["value"] == 1204


# ---------------------------------------------------------------------------
# 3. Nothing the page chose can leave
# ---------------------------------------------------------------------------


def test_the_verdict_function_carries_no_plant_out_in_a_value_or_a_raise():
    for reading in [
        None,
        {"elements": PLANT, "matches": PLANT},
        {"elements": 3, "matches": [{"phrase": PLANT, "shape": PLANT, "value": PLANT}]},
        {"elements": 3, "matches": [PLANT, None, 7]},
    ]:
        try:
            out = company_root.connection_counts(reading)
        except Exception as exc:  # noqa: BLE001 -- a raise is a failure here
            pytest.fail(f"connection_counts raised {type(exc).__name__}: {exc}")
        assert carries_the_plant(out) == []


def test_the_control_a_bare_int_would_have_carried_the_plant_out():
    """SHOWN FAILING, on the coercion that actually shipped elsewhere."""
    with pytest.raises(ValueError) as caught:
        int(PLANT)
    assert PLANT in str(caught.value)
    assert coerce.as_int(PLANT) is None


async def test_the_reader_driven_by_a_page_that_answers_in_names_is_clean():
    out = await company_root.read_company_root(PlantedPage())
    assert carries_the_plant(out) == []
    assert isinstance(out["elements"], int)
    assert out["matches"] == [] or all(
        isinstance(value, int)
        for row in out["matches"]
        for value in row.values()
    )
    assert out["values_refused"] > 0


async def test_the_reader_never_raises_on_a_page_that_answers_in_names():
    await company_root.read_company_root(PlantedPage(), html=PLANT)


def test_the_emitted_alphabet_covers_every_token_a_caller_can_receive():
    """Driven over every position and every shape, in range and out of it."""
    readings = [None, {}, {"elements": 9, "chunks": 2, "matches": []},
                {"elements": 0, "matches": []}]
    for position in range(-1, len(company_root.COUNT_PHRASES) + 1):
        for shape in range(-1, len(company_root.NUMERAL_SHAPES) + 1):
            readings.append(
                {
                    "elements": 9,
                    "chunks": 2,
                    "matches": [
                        {
                            "phrase": position,
                            "shape": shape,
                            "value": 1,
                            "chars": 9,
                        }
                    ],
                }
            )

    tokens = set()
    for reading in readings:
        out = company_root.connection_counts(reading)
        for entry in out["by_kind"].values():
            tokens.add(entry["state"])
            if entry["numeral"] is not None:
                tokens.add(entry["numeral"])
    for position in range(-1, len(company_root.COUNT_PHRASES) + 1):
        tokens.add(company_root.kind_for(position))
    for shape in range(-1, len(company_root.NUMERAL_SHAPES) + 1):
        tokens.add(company_root.term_for(shape))
    assert tokens <= company_root.emitted_alphabet(), (
        tokens - company_root.emitted_alphabet()
    )


# ---------------------------------------------------------------------------
# 4. The signatures
# ---------------------------------------------------------------------------


def test_only_one_function_here_touches_a_page_and_none_takes_a_needle():
    async_functions = [
        name
        for name, function in vars(company_root).items()
        if inspect.isfunction(function) and inspect.iscoroutinefunction(function)
    ]
    assert async_functions == ["read_company_root"], async_functions

    banned = {"name", "url", "href", "slug", "query", "keywords", "company"}
    for name, function in vars(company_root).items():
        if not inspect.isfunction(function):
            continue
        parameters = set(inspect.signature(function).parameters)
        assert not (parameters & banned), (name, parameters)


def test_the_module_fires_nothing():
    for name, function in vars(company_root).items():
        if not inspect.isfunction(function):
            continue
        parameters = set(inspect.signature(function).parameters)
        assert not (parameters & {"confirm_token", "token", "grant"}), name


def test_the_address_is_admitted_and_the_roster_tab_still_is_not():
    """This reader opens the ROOT. The member roster stays shut."""
    built = company_page.company_page_url(IDENTIFIER)
    assert built["built"] is True
    assert readonly.is_read_url(built["url"]) is True
    assert (
        readonly.is_read_url(
            f"https://www.linkedin.com/company/{IDENTIFIER}/people/"
        )
        is False
    )
    assert company_page.company_page_url(EPONYMOUS_SLUG)["built"] is False


def test_company_page_still_opens_nothing():
    """The vocabulary module's own claim survives this reader being built.

    ``company_page.py`` says *"It opens nothing. There is no page function
    here"* and its own test refuses any coroutine in it. The reading lives in
    a separate module for that reason, and this asserts the separation from
    the other side.
    """
    assert not any(
        inspect.iscoroutinefunction(function)
        for function in vars(company_page).values()
        if inspect.isfunction(function)
    )


# ---------------------------------------------------------------------------
# 5. THE SHIPPED SCRIPT UNDER V8, AND THE DEFECT THAT CHANGES ITS ANSWER
# ---------------------------------------------------------------------------

#: The one line in the shipped script that steps over a screen-reader subtree,
#: and the line that steps over nothing. The replacement is applied to a COPY
#: of the script source; the module is never edited.
_SKIP = "if (isHidden(child)) { skipped += 1; continue; }"
_BLIND = "if (false) { skipped += 1; continue; }"

#: A minimal node tree, built in the driver because node has no DOM. It
#: implements exactly the five things the shipped walk uses -- ``nodeType``,
#: ``childNodes``, ``nodeValue``, ``matches`` and the document's ``body`` --
#: and ``matches`` understands class selectors, which is all
#: ``CARD_HIDDEN_SELECTOR`` is made of. The TREE it builds comes from
#: ``company_root.control_tree()``, so the offline control and the in-page
#: control are the same fixture rather than two copies of one.
#: A NODE'S FIRST FIELD IS A CLASS LIST, OR A TAG NAME WHEN IT IS ALL CAPS.
#: That convention exists so the corpus can model a ``<script>`` -- a node a
#: browser never draws as text -- without the harness growing a second tree
#: format. It is named here because a convention nobody wrote down is a
#: convention the next reader gets wrong.
_BUILDER = """
const T = (s) => ({ nodeType: 3, nodeValue: s, childNodes: [] });
const isTag = (s) => !!s && s === s.toUpperCase() && s !== s.toLowerCase();
const E = (cls, kids) => ({
  nodeType: 1,
  childNodes: kids,
  tagName: isTag(cls) ? cls : "DIV",
  hasAttribute: () => false,
  matches: (sel) => {
    if (isTag(cls)) return false;
    const wanted = sel.split(",").map((s) => s.trim());
    const mine = (cls || "").split(" ");
    for (let i = 0; i < mine.length; i += 1) {
      if (mine[i] && wanted.indexOf("." + mine[i]) !== -1) return true;
    }
    return false;
  },
});
const build = (node) => E(node[0], node[1].map(
  (kid) => (typeof kid === "string" ? T(kid) : build(kid))
));
globalThis.document = { body: build(TREE) };
"""


def _node() -> str | None:
    return shutil.which("node")


def _jsonable(node):
    klass, children = node
    return [
        klass,
        [kid if isinstance(kid, str) else _jsonable(kid) for kid in children],
    ]


def _run_in_node(script_source: str, tree=None) -> dict:
    """Run a COUNT_LINES_JS source under V8 over a tree, the shipped one by
    default."""
    driver = (
        "const TREE = %s;\n%s\nconst run = %s;\n"
        "console.log(JSON.stringify(run(%s)));\n"
        % (
            json.dumps(
                _jsonable(
                    company_root.control_tree() if tree is None else tree
                )
            ),
            _BUILDER,
            script_source,
            json.dumps(
                {
                    "phrases": company_root.phrases_shipped(),
                    "hidden": dom.CARD_HIDDEN_SELECTOR,
                    "html": "",
                    "maxDepth": dom.COUNT_LINES_MAX_DEPTH,
                    "maxChunks": dom.COUNT_LINES_MAX_CHUNKS,
                    "maxChunkChars": dom.COUNT_LINES_MAX_CHUNK_CHARS,
                    "maxDigits": dom.COUNT_LINES_MAX_DIGITS,
                    "maxGap": dom.COUNT_LINES_MAX_NUMERAL_GAP,
                }
            ),
        )
    )
    handle, path = tempfile.mkstemp(suffix=".mjs")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(driver)
        proc = subprocess.run(
            [_node(), path], capture_output=True, text=True
        )
    finally:
        os.remove(path)
    assert proc.returncode == 0, proc.stderr[:2000]
    return json.loads(proc.stdout)


def _verdict(raw: dict) -> dict:
    """Feed a raw in-page reading through the shipped Python side."""
    return company_root.connection_counts(
        {
            "elements": raw["elements"],
            "chunks": raw["chunks"],
            "chunks_capped": raw["chunks_capped"],
            "hidden_subtrees_skipped": raw["hidden_skipped"],
            "non_content_skipped": raw["non_content_skipped"],
            "matches": raw["matches"],
            "matches_refused": 0,
        }
    )


def test_the_planted_defect_anchor_is_still_in_the_shipped_script():
    """A control whose plant no longer applies is a control of nothing."""
    assert dom.COUNT_LINES_JS.count(_SKIP) == 1, (
        "the line this control plants a defect into has moved. Repoint it; do "
        "not delete the control -- it is the only thing standing between this "
        "reader and the accessible copy."
    )


def test_the_shipped_script_reads_the_visible_line_and_not_the_hidden_one():
    if _node() is None:
        pytest.skip(
            "THE CROSS-ENGINE CONTROL DID NOT RUN: node is not on PATH, so "
            "the shipped in-page script was not exercised at all on this run"
        )
    raw = _run_in_node(dom.COUNT_LINES_JS)
    out = _verdict(raw)
    expected = company_root.control_expectations()

    assert out["hidden_subtrees_skipped"] == expected["hidden_subtrees_skipped"]
    for kind, wanted in expected.items():
        if kind == "hidden_subtrees_skipped":
            continue
        got = out["by_kind"][kind]
        assert got["state"] == wanted["state"], (kind, got)
        assert got["value"] == wanted["value"], (kind, got)
        assert got["numeral"] == wanted["numeral"], (kind, got)


def test_the_defect_that_reads_the_accessible_copy_changes_the_answer():
    """SHOWN FAILING. Remove the skip and the reader says FORTY-ONE.

    This is the measured search-card hazard arriving on this surface: the
    screen-reader copy is terser than the visible line, so it is the TIGHTEST
    container carrying the phrase, so it wins -- and it carries a different
    number. A walk on ``textContent`` publishes it as the answer.
    """
    if _node() is None:
        pytest.skip(
            "THE CROSS-ENGINE CONTROL DID NOT RUN: node is not on PATH, so "
            "the defect was never planted and this file proves nothing about "
            "the accessible copy"
        )
    defective = _verdict(_run_in_node(dom.COUNT_LINES_JS.replace(_SKIP, _BLIND)))
    got = defective["by_kind"]["connections_at_organisation"]
    assert got["value"] == 41, got
    assert defective["hidden_subtrees_skipped"] == 0

    shipped = _verdict(_run_in_node(dom.COUNT_LINES_JS))
    assert shipped["by_kind"]["connections_at_organisation"]["value"] == 11


def test_neither_build_carries_the_plant_out_which_is_the_honest_half():
    """The skip buys a CORRECT NUMBER. Name-freedom is bought one layer down.

    Saying so matters: a control that let the leak and the miscount ride on
    one line would let somebody remove the skip and believe they had only
    loosened an accuracy check.
    """
    if _node() is None:
        pytest.skip("node is not on PATH; the in-page script was not driven")
    plant = "Exampleone Markersurname"
    for source in (dom.COUNT_LINES_JS, dom.COUNT_LINES_JS.replace(_SKIP, _BLIND)):
        rendered = json.dumps(_verdict(_run_in_node(source)))
        assert plant not in rendered


def test_an_abbreviation_and_a_decimal_are_both_refused_in_the_page():
    """The two numerals that look right and are not, measured under V8."""
    if _node() is None:
        pytest.skip("node is not on PATH; the in-page script was not driven")
    raw = _run_in_node(dom.COUNT_LINES_JS)
    shapes = {
        company_root.term_for(row["shape"]) for row in raw["matches"]
    }
    assert "abbreviated_refused" in shapes, raw["matches"]
    assert "decimal_refused" in shapes, raw["matches"]


def test_the_script_declares_no_mutating_token():
    """The scan that every executed script is held to, asserted here too."""
    assert readonly.scan_js_for_mutations(dom.COUNT_LINES_JS) == []


def test_the_control_fixture_and_the_control_tree_are_one_fixture():
    """Rendered from one structure, so the two cannot drift apart."""
    markup = company_root.control_fixture()
    for text in _flat_text(company_root.control_tree()):
        assert text in markup, text


def _flat_text(node):
    _klass, children = node
    for child in children:
        if isinstance(child, str):
            yield child
        else:
            yield from _flat_text(child)


def test_the_fixture_carries_a_person_shaped_plant_rather_than_a_placeholder():
    """A fixture whose hazard is spelled ``xxx`` does not exercise the hazard."""
    markup = company_root.control_fixture()
    assert "Markersurname" in markup


# ---------------------------------------------------------------------------
# 6. THE AUTHWALL REFUSAL, AND THE SHIPPED ONE SHOWN PUBLISHING A SLUG
# ---------------------------------------------------------------------------

#: A signed-out bounce from an organisation Page. LinkedIn's authwall carries
#: the address it bounced INSIDE ITS OWN QUERY, and the canonical form of an
#: organisation address is a SLUG -- which is a name. Synthetic, person-shaped.
AUTHWALL_CARRYING_A_SLUG = (
    "https://www.linkedin.com/authwall?sessionRedirect="
    "https%3A%2F%2Fwww.linkedin.com%2Fcompany%2F"
    "exampleone-markersurname-associates%2F"
)


def test_the_shipped_authwall_refusal_publishes_the_slug_it_bounced():
    """SHOWN FAILING, against the SHIPPED function, not a mutant.

    This is the control that makes the test below a measurement rather than a
    green. ``auth.assert_not_authwall`` interpolates the FINAL url into its
    message; that message reaches ``server._error``; ``config.scrub``
    substitutes this server's own FILESYSTEM PATHS and nothing else. So the
    slug arrives at the caller intact -- in an exception, which is not a
    return value.

    **IT IS NOT A DEFECT IN THAT FUNCTION AND IS NOT FIXED HERE.** Every other
    tool in the package bounces the same way and most of their addresses carry
    a numeric id. The divergence is scoped to the two surfaces where the
    landing can be a name.
    """
    from linkedin_server import server
    from linkedin_server.auth import assert_not_authwall
    from linkedin_server.errors import NotAuthenticatedError

    with pytest.raises(NotAuthenticatedError) as caught:
        assert_not_authwall(AUTHWALL_CARRYING_A_SLUG, surface="organisation Page")
    rendered = json.dumps(server._error(caught.value))
    assert "exampleone-markersurname" in rendered, (
        "the shipped refusal no longer publishes its landing, so the "
        "divergence below is buying nothing and should be removed"
    )


def test_the_new_surfaces_refuse_without_naming_what_they_bounced_off():
    """The same input, through the helper the two new tools call."""
    from linkedin_server import server
    from linkedin_server.errors import NotAuthenticatedError

    for surface in ("organisation Page", "group page"):
        with pytest.raises(NotAuthenticatedError) as caught:
            server._authwall_refusal_without_the_landing(
                AUTHWALL_CARRYING_A_SLUG, surface=surface
            )
        exception = caught.value
        rendered = json.dumps(server._error(exception))
        assert "exampleone-markersurname" not in rendered, rendered
        assert "authwall?" not in rendered, rendered
        assert "sessionRedirect" not in rendered, rendered
        # ``from None`` is part of the fix: a traceback rendered anywhere must
        # not be able to walk back to the message that held the url.
        assert exception.__cause__ is None
        assert exception.__suppress_context__ is True


def test_the_helper_lets_a_signed_in_landing_through():
    """A gate that refuses everything is not discriminating, it is failing."""
    from linkedin_server import server

    server._authwall_refusal_without_the_landing(
        "https://www.linkedin.com/company/5417062/", surface="organisation Page"
    )


def test_the_helper_is_not_on_the_tool_surface():
    """A private helper that became a tool is a defect this repo has met."""
    import asyncio

    from linkedin_server import server

    names = {tool.name for tool in asyncio.run(server.mcp.list_tools())}
    assert "_authwall_refusal_without_the_landing" not in names


# ---------------------------------------------------------------------------
# 7. THE SHAPES A COLD REVIEW CONVICTED, DRIVEN ROW BY ROW UNDER V8
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "row", company_root.adversarial_trees(), ids=lambda row: row[0]
)
def test_every_shape_a_cold_review_convicted_reads_correctly_now(row):
    """FOUR OF THESE WERE REDS, and two are the boundary either side of one.

    The first version of the shipped script took the FIRST digit run in a
    candidate line, so "50 people viewed, 11 connections work here" published
    FIFTY -- out of the one path the module claimed could not produce a wrong
    number. It also preferred a SHORTER phrase-only match over the parent
    holding the count, so an ordinary stat line read numeral_refused.

    Both are driven here against the SHIPPED constant rather than described.
    """
    if _node() is None:
        pytest.skip(
            "THE CROSS-ENGINE CONTROL DID NOT RUN: node is not on PATH, so "
            "none of the shapes this corpus exists for were exercised"
        )
    label, tree, expected_value, expected_shape = row
    verdict = _verdict(_run_in_node(dom.COUNT_LINES_JS, tree))
    got = verdict["by_kind"]["connections_at_organisation"]

    if expected_value < 0:
        assert got["value"] is None, (label, got)
        if expected_shape == "phrase_not_drawn":
            assert got["state"] == "phrase_not_drawn", (label, got)
        else:
            assert got["state"] == "numeral_refused", (label, got)
            assert got["numeral"] == expected_shape, (label, got)
    else:
        assert got["state"] == "count_read", (label, got)
        assert got["value"] == expected_value, (label, got)
        assert got["numeral"] == expected_shape, (label, got)


def test_the_first_digit_run_rule_is_shown_reading_the_wrong_number():
    """SHOWN FAILING, on the exact defect, by restoring the old rule.

    The repaired script finds the numeral by its DISTANCE FROM THE PHRASE. Put
    the old rule back -- read the numeral from the start of the line -- and the
    same tree publishes FIFTY. Applied to a COPY of the source; the module is
    never edited.
    """
    if _node() is None:
        pytest.skip("node is not on PATH; the in-page script was not driven")

    old_rule = "const num = numeralOf(text);"
    repaired = "const num = numeralNear(text, rawStart, rawEnd);"
    assert dom.COUNT_LINES_JS.count(repaired) == 1, (
        "the line this control plants a defect into has moved. Repoint it; do "
        "not delete the control -- it is the only thing standing between this "
        "reader and a wrong number that looks right."
    )
    tree = company_root.adversarial_trees()[0][1]
    defective = _verdict(
        _run_in_node(dom.COUNT_LINES_JS.replace(repaired, old_rule), tree)
    )
    got = defective["by_kind"]["connections_at_organisation"]
    assert got["state"] == "count_read"
    assert got["value"] == 50, got

    shipped = _verdict(_run_in_node(dom.COUNT_LINES_JS, tree))
    assert shipped["by_kind"]["connections_at_organisation"]["value"] == 11


def test_the_length_only_preference_is_shown_losing_the_count():
    """SHOWN FAILING, on the second defect, by restoring the old preference.

    Length as the RULE rather than the tie-break makes a span holding the
    phrase alone beat the parent holding the phrase AND the number.
    """
    if _node() is None:
        pytest.skip("node is not on PATH; the in-page script was not driven")

    repaired = """      if (prior) {
        const priorHas = prior.shape !== SHAPE_NONE;
        const mineHas = num.shape !== SHAPE_NONE;
        if (priorHas && !mineHas) continue;
        if (priorHas === mineHas && prior.len <= text.length) continue;
      }"""
    old_rule = """      if (prior && prior.len <= text.length) continue;"""
    assert dom.COUNT_LINES_JS.count(repaired) == 1, (
        "the preference rule this control plants a defect into has moved"
    )
    tree = company_root.adversarial_trees()[1][1]
    defective = _verdict(
        _run_in_node(dom.COUNT_LINES_JS.replace(repaired, old_rule), tree)
    )
    got = defective["by_kind"]["connections_at_organisation"]
    assert got["state"] == "numeral_refused", got
    assert got["value"] is None

    shipped = _verdict(_run_in_node(dom.COUNT_LINES_JS, tree))
    assert shipped["by_kind"]["connections_at_organisation"]["value"] == 11


def test_aria_hidden_is_deliberately_not_stepped_over():
    """THE MEASURED INVERSION, asserted so nobody "improves" it.

    On the search card the VISIBLE span is the one wearing aria-hidden and the
    screen-reader duplicate is the one carrying a name. A walk that skipped
    aria-hidden would step over exactly the copy this reader wants.
    """
    assert "aria-hidden" not in dom.CARD_HIDDEN_SELECTOR
    assert 'hasAttribute("aria-hidden")' not in dom.COUNT_LINES_JS
    assert 'ARIA-HIDDEN IS DELIBERATELY NOT ON THIS LIST' in dom.COUNT_LINES_JS


# ---------------------------------------------------------------------------
# 8. THE ARGUMENT ITSELF IS COERCED, NOT ONLY ITS FIELDS
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "reading", [1, True, False, 0, PLANT, b"bytes", 3.5, [1, 2], {1, 2}, object()]
)
def test_the_verdict_functions_never_raise_on_a_non_mapping(reading):
    """``dict(reading or {})`` RAISED on a bare int, bool or string.

    Every FIELD was coerced and the ARGUMENT was not -- the coercion-leak class
    one layer shallower, in two functions whose docstrings say a needle cannot
    reach them. Found by a cold review; no caller in this package could reach
    it, which is a fact about today's callers and not about the function.
    """
    from linkedin_server import group_page

    for function in (company_root.connection_counts, group_page.reachability):
        try:
            out = function(reading)
        except Exception as exc:  # noqa: BLE001 -- a raise is the failure
            pytest.fail(f"{function.__name__} raised {type(exc).__name__}: {exc}")
        assert carries_the_plant(out) == []


def test_control_swapping_the_alphabet_fabricates_a_trusted_number(monkeypatch):
    """SHOWN FAILING. Put ``plain_digits`` at index 0 and a REFUSED value
    becomes a number nobody read.

    The assertion above states a property; this drives the defect it exists
    to catch. ``coerce`` substitutes a refused value with ``0``, so index 0 is
    where garbage lands -- and with a value-bearing class there, a page that
    answered a shape slot with a string publishes ``count_read`` and a figure.

    Monkeypatched rather than edited, because several agents write this tree
    and mutating a shipped constant even briefly can be picked up.
    """
    swapped = ("plain_digits", "no_digit_run") + company_root.NUMERAL_SHAPES[2:]
    monkeypatch.setattr(company_root, "NUMERAL_SHAPES", swapped)
    verdict = company_root.connection_counts(
        {
            "elements": 40,
            "chunks": 9,
            "matches": [{"phrase": 0, "shape": 0, "value": 99, "chars": 12}],
        }
    )["by_kind"]["connections_at_organisation"]
    assert verdict["state"] == "count_read", verdict
    assert verdict["value"] == 99, (
        "the swap did not fabricate a number, so the ordering assertion above "
        "is not standing for anything"
    )


def test_control_the_non_mapping_argument_used_to_raise():
    """SHOWN FAILING, on the expression that shipped.

    ``dict(reading or {})`` is what both verdict functions opened with. The
    repaired form is an ``isinstance`` check; this drives the OLD expression
    over the same inputs so the repair is a measurement rather than a claim.
    """
    for reading in (1, True, PLANT):
        with pytest.raises((TypeError, ValueError)):
            dict(reading or {})  # the shipped expression, before the repair
    # And the repaired shape swallows every one of them.
    for reading in (1, True, PLANT):
        assert (reading if isinstance(reading, dict) else {}) == {}
