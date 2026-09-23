"""`scripts/_probe_disclosure_targets.py`'s injected reader, run over a real DOM.

WHY THIS RUNS A REAL BROWSER. The probe's whole claim is about what
`document.querySelectorAll("[aria-expanded]")` and its sibling actually
resolve, in what order, with what ancestors -- and that is exactly the kind
of thing a hand-written Python fixture cannot exercise. So this launches a
throwaway LOCAL headless Chromium (never the operator's, never the
persistent profile -- the same pattern `tests/test_profile_views_fixture.py`
uses for the real injected harvester) and runs the probe's own
`DISCLOSURE_TARGETS_JS` against a synthetic document built to exercise every
branch the probe's docstring claims: landmark ancestry, `in_main`/`in_form`,
`item_ordinal` against a feed-item-shaped container, the single-word-versus-
multi-word phrase rule, an `aria-controls` target that is hidden and carries
numeric paragraphs, a `data-view-name` that is shape-valid and one that is
not, and a `<select>`'s option terms.

NO REAL PERSON, EMPLOYER, CITY, MEMBER ID OR PROFILE SLUG APPEARS ANYWHERE
BELOW. Every name-shaped string is an obviously synthetic nonsense token
("Zqxv Wbnmk", "Qrtplex Holdings", ...), and the closed-alphabet assertions
below exist precisely to prove those tokens never reach the probe's output --
so this file's own literals double as the adversarial input.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

_PROBE_PATH = REPO / "scripts" / "_probe_disclosure_targets.py"


def _probe_module():
    """Import the probe by path, fresh, matching this repo's convention for
    ``_probe_*.py`` files (see ``tests/test_otw_payload_probe.py``,
    ``tests/test_unfired_probe_verdicts.py``). The import itself does
    nothing -- ``tests/test_scripts_are_import_safe.py`` asserts that for
    every script, and this exercises it once more for free.
    """
    spec = importlib.util.spec_from_file_location(
        "_probe_disclosure_targets", _PROBE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# The synthetic tokens. Obviously invented, and named as such -- not one of
# these is a real person, company, or place. Used as adversarial input: every
# one must vanish from the probe's output under classification.
# ---------------------------------------------------------------------------

SYNTH_PERSON_A = "Zqxv Wbnmk"
SYNTH_PERSON_B = "Qrtplex Vundo"
SYNTH_COMPANY_A = "Qrtplex Holdings"
SYNTH_COMPANY_B = "Zqxv Industries"
SYNTH_FAMILY = "Qrtplex Foundation"

SYNTHETIC_TOKENS: tuple[str, ...] = (
    SYNTH_PERSON_A, SYNTH_PERSON_B, SYNTH_COMPANY_A, SYNTH_COMPANY_B,
    SYNTH_FAMILY,
)

#: The label the "open control menu" multi-word phrase must be found
#: CONTAINED within, carrying a synthetic name it must not leak.
LABEL_POST_CONTROL_MENU = "Open control menu for post by " + SYNTH_PERSON_A
#: A label that must NOT whole-match "send" (six words, "send" is not the
#: whole label) and must not leak the name it carries either.
LABEL_SEND_TO_PERSON = "Send a message to " + SYNTH_PERSON_B
#: The single-word-rule pair for "me".
LABEL_ME = "Me"
LABEL_ME_PLUS = "Me " + SYNTH_FAMILY
#: The single-word-rule pair for "company".
LABEL_COMPANY = "Company"
LABEL_COMPANY_PLUS = "Company " + SYNTH_COMPANY_A
#: The aria-controls target's hidden panel content -- carries a name in its
#: own right, through the `<p>` numeric check as well as an id.
CONTROLS_TARGET_TEXT = SYNTH_PERSON_A + " at " + SYNTH_COMPANY_A
#: The two select options -- company names, classified and never emitted.
OPTION_A = SYNTH_COMPANY_A
OPTION_B = SYNTH_COMPANY_B
#: data-view-name pair: one shape-valid (survives verbatim -- it is
#: LinkedIn's own internal component-naming vocabulary, not a person), one
#: not (a person's name, correctly refused to "<unshaped>").
VIEW_NAME_SHAPED = "search-filter-top-bar-select"
VIEW_NAME_UNSHAPED = SYNTH_PERSON_A


FIXTURE_HTML = """
<!DOCTYPE html>
<html><body>
<header>
  <button aria-expanded="false">Menu</button>
</header>
<nav>
  <button aria-haspopup="menu">Jump</button>
</nav>
<main>
  <div data-urn="feed-item-a">
    <button aria-expanded="true" aria-label="%(post_control_menu)s">X</button>
  </div>
  <form>
    <button aria-expanded="mixed">Submit</button>
  </form>
  <div data-urn="feed-item-b">
    <button aria-haspopup="true" aria-label="%(send_to_person)s">S</button>
  </div>
  <button aria-expanded="false" aria-label="%(me)s">P</button>
  <button aria-expanded="false" aria-label="%(me_plus)s">P2</button>
  <button aria-haspopup="dialog" aria-label="%(company)s">F</button>
  <button aria-haspopup="dialog" aria-label="%(company_plus)s">F2</button>
  <span id="lbl-1">Share</span>
  <button aria-haspopup="true" aria-labelledby="lbl-1">L</button>
  <button aria-haspopup="weird">O</button>
  <button aria-expanded="false" data-view-name="%(view_shaped)s">V</button>
  <button aria-expanded="false" data-view-name="%(view_unshaped)s">V2</button>
  <div data-view-name="holder-region-one">
    <button aria-expanded="false">H</button>
  </div>
  <button aria-expanded="false" class="alpha-cls beta-cls gamma-cls delta-cls epsilon-cls zeta-cls eta-cls bad999999 zz">C</button>
  <button aria-expanded="false" aria-controls="hidden-panel">Ctl</button>
  <div id="hidden-panel" hidden>
    <p>42%%</p><p>1,234</p><p>%(controls_target_text)s</p>
  </div>
  <select aria-expanded="false">
    <option>%(option_a)s</option>
    <option>%(option_b)s</option>
  </select>
  <button aria-expanded="false" role="%(synth_role)s">R</button>
  <div style="display:none">
    <button aria-expanded="false">Hidden</button>
  </div>
</main>
<button aria-expanded="false">Orphan</button>
</body></html>
""" % {
    "post_control_menu": LABEL_POST_CONTROL_MENU,
    "send_to_person": LABEL_SEND_TO_PERSON,
    "me": LABEL_ME,
    "me_plus": LABEL_ME_PLUS,
    "company": LABEL_COMPANY,
    "company_plus": LABEL_COMPANY_PLUS,
    "view_shaped": VIEW_NAME_SHAPED,
    "view_unshaped": VIEW_NAME_UNSHAPED,
    "option_a": OPTION_A,
    "option_b": OPTION_B,
    "controls_target_text": CONTROLS_TARGET_TEXT,
    "synth_role": SYNTH_PERSON_A,
}


async def _read_fixture():
    """Launch a local headless Chromium, load the fixture, run the probe's
    own script with its own cfg builder. Returns ``(probe_module, result)``.
    """
    playwright = pytest.importorskip("playwright.async_api")
    probe = _probe_module()
    async with playwright.async_playwright() as pw:
        engine = await pw.chromium.launch(headless=True)
        try:
            tab = await engine.new_page()
            await tab.set_content(
                FIXTURE_HTML, wait_until="domcontentloaded", timeout=60_000
            )
            pw_expanded = await tab.locator(probe.SHAPE_EXPANDED).count()
            pw_haspopup = await tab.locator(probe.SHAPE_HASPOPUP).count()
            result = await tab.evaluate(
                probe.DISCLOSURE_TARGETS_JS, probe._build_cfg()
            )
        finally:
            await engine.close()
    return probe, result, pw_expanded, pw_haspopup


# ---------------------------------------------------------------------------
# (a) record count and order match document order, and every named placement
# from the brief is present: header, nav, two-plus in main, one in a form,
# one inside a feed-item-shaped [data-urn] container.
# ---------------------------------------------------------------------------


async def test_record_count_matches_playwrights_own_locator():
    _probe, result, pw_expanded, pw_haspopup = await _read_fixture()
    expanded = result["expanded"]["records"]
    haspopup = result["haspopup"]["records"]
    assert len(expanded) == pw_expanded == 14, (len(expanded), pw_expanded)
    assert len(haspopup) == pw_haspopup == 6, (len(haspopup), pw_haspopup)
    # order_basis_ok is exactly this equality -- proven here independently of
    # the probe's own computation of it.
    assert [r["idx"] for r in expanded] == list(range(len(expanded)))
    assert [r["idx"] for r in haspopup] == list(range(len(haspopup)))


async def test_header_nav_main_form_and_feed_item_placements():
    _probe, result, _pw_e, _pw_h = await _read_fixture()
    expanded = result["expanded"]["records"]
    haspopup = result["haspopup"]["records"]

    # ONE IN HEADER (expanded[0]), document order.
    assert expanded[0]["landmark"] == "header"
    assert expanded[0]["in_main"] is False
    assert expanded[0]["in_form"] is False

    # ONE IN NAV (haspopup[0]).
    assert haspopup[0]["landmark"] == "nav"

    # THE FEED-ITEM-SHAPED [data-urn] CONTAINER, ONE PER SHAPE, each the
    # first item container in the document -- expanded's comes first in the
    # markup, haspopup's second, so ordinals are 0 and 1 respectively.
    assert expanded[1]["landmark"] == "main"
    assert expanded[1]["in_main"] is True
    assert expanded[1]["item_ordinal"] == 0
    assert haspopup[1]["landmark"] == "main"
    assert haspopup[1]["item_ordinal"] == 1

    # ONE INSIDE A FORM, and it is still inside main (a <form> is not a
    # landmark tag or role).
    assert expanded[2]["in_form"] is True
    assert expanded[2]["landmark"] == "main"
    assert expanded[2]["in_main"] is True

    # TWO-PLUS IN MAIN: every remaining expanded/haspopup record but the
    # header/nav/orphan ones.
    main_expanded = [r for r in expanded if r["landmark"] == "main"]
    assert len(main_expanded) >= 2

    # THE LANDMARK-NONE CASE, so "none" is proven reachable and not merely
    # the default nobody exercises.
    assert expanded[-1]["landmark"] == "none"
    assert expanded[-1]["in_main"] is False
    assert expanded[-1]["in_form"] is False

    # ITEM CONTAINERS OUTSIDE ANY [data-urn]/[data-id] read -1, not 0 or null.
    assert expanded[0]["item_ordinal"] == -1
    assert expanded[-1]["item_ordinal"] == -1


# ---------------------------------------------------------------------------
# (c) THE CLOSED ALPHABET: no synthetic token anywhere in the dump, every
# matched term is a VOCABULARY key, unmatched records carry only shape facts.
# ---------------------------------------------------------------------------


async def test_no_synthetic_token_anywhere_in_the_dump():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    dumped = json.dumps(result)
    for token in SYNTHETIC_TOKENS:
        assert token not in dumped, token
    # AND THE COMPOUND FORM, so a leak that only shows up when two names sit
    # beside each other (the hidden-controls target's text) is not missed by
    # checking each name alone.
    assert CONTROLS_TARGET_TEXT not in dumped


async def test_every_matched_term_is_a_vocabulary_key():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    seen_matched = False
    seen_unmatched = False
    for shape_key in ("expanded", "haspopup"):
        for record in result[shape_key]["records"]:
            term = record["term"]
            if "term" in term:
                assert term["term"] in probe.VOCABULARY, term
                seen_matched = True
            else:
                # UNMATCHED RECORDS CARRY ONLY SHAPE FACTS.
                assert set(term) == {
                    "refused", "band", "tokens", "has_digits", "all_capitalised",
                } or set(term) == {"refused"}, term
                assert term["refused"] in probe.REFUSAL_KEYS, term
                seen_unmatched = True
            if record.get("tag") == "select":
                for opt_term in record.get("option_terms", []):
                    if "term" in opt_term:
                        assert opt_term["term"] in probe.VOCABULARY, opt_term
                    else:
                        assert opt_term["refused"] in probe.REFUSAL_KEYS, opt_term
    assert seen_matched, "the fixture produced no matched term at all"
    assert seen_unmatched, "the fixture produced no unmatched record at all"


# ---------------------------------------------------------------------------
# (d) THE SINGLE-WORD RULE
# ---------------------------------------------------------------------------


async def test_single_word_terms_require_the_whole_label():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    expanded = result["expanded"]["records"]
    haspopup = result["haspopup"]["records"]

    assert expanded[3]["term"] == {"term": "nav_me"}
    assert "term" not in expanded[4]["term"]
    assert expanded[4]["term"]["refused"] == "unmatched"

    assert haspopup[2]["term"] == {"term": "company_filter"}
    assert "term" not in haspopup[3]["term"]
    assert haspopup[3]["term"]["refused"] == "unmatched"

    # THE MULTI-WORD CONTAINED CASE, on the same fixture.
    assert expanded[1]["term"] == {"term": "post_control_menu"}

    # aria-labelledby resolves to the referenced element's text, and a
    # single-word phrase still requires the WHOLE resolved label.
    assert haspopup[4]["term"] == {"term": "share"}


# ---------------------------------------------------------------------------
# (e) a hidden aria-controls target with two numeric <p> children
# ---------------------------------------------------------------------------


async def test_hidden_controls_target_with_two_numeric_paragraphs():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    # The button with aria-controls="hidden-panel" is expanded[9] -- the
    # fixture places it right after the classes-test button, before the
    # <select>.
    record = None
    for candidate in result["expanded"]["records"]:
        if candidate["controls"]["present"]:
            record = candidate
            break
    assert record is not None, "no record carried aria-controls at all"
    controls = record["controls"]
    assert controls["target_found"] is True
    assert controls["target_hidden"] is True
    assert controls["numeric_p"] == 2
    assert controls["text_band"] != "0"


# ---------------------------------------------------------------------------
# (f) data-view-name: shape-valid survives verbatim, a person's name refuses
# ---------------------------------------------------------------------------


async def test_data_view_name_shape_rule():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    expanded = result["expanded"]["records"]

    shaped = [r for r in expanded if r["own_view"] == VIEW_NAME_SHAPED]
    assert len(shaped) == 1, expanded
    assert shaped[0]["own_view"] == "search-filter-top-bar-select"

    unshaped = [r for r in expanded if r["own_view"] == "<unshaped>"]
    assert len(unshaped) == 1, expanded
    # AND THE NAME ITSELF NEVER SURVIVES -- own_view is the sentinel, not the
    # person's name that produced it. Covered again by the whole-dump sweep
    # above; asserted narrowly here too because this is the exact field.
    assert VIEW_NAME_UNSHAPED not in json.dumps(expanded)

    # THE HOLDER-VIEW CASE: nested one level under a data-view-name'd div.
    holder = [r for r in expanded if r["holder_view"] == "holder-region-one"]
    assert len(holder) == 1, expanded
    assert holder[0]["holder_depth"] == 1
    assert holder[0]["own_view"] is None


# ---------------------------------------------------------------------------
# `role` / `type`: same shape discipline as own_view -- a synthetic person's
# name in `role` must refuse to "<unshaped>" and never survive the dump.
# ---------------------------------------------------------------------------


async def test_role_is_shape_confined_like_own_view():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    expanded = result["expanded"]["records"]

    # THE ONLY record in this fixture carrying a `role` attribute at all is
    # the one built for this test, so the search is unambiguous.
    role_bearing = [r for r in expanded if r["role"] is not None]
    assert len(role_bearing) == 1, expanded
    assert role_bearing[0]["role"] == "<unshaped>"

    # AND THE NAME ITSELF NEVER SURVIVES -- same discipline, same proof shape
    # as the own_view / closed-alphabet checks above.
    assert SYNTH_PERSON_A not in json.dumps(expanded)


# ---------------------------------------------------------------------------
# `visible`: a press can only land on a rendered control.
# ---------------------------------------------------------------------------


async def test_visible_is_false_for_a_display_none_ancestor():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    expanded = result["expanded"]["records"]

    # EXACTLY ONE record in this fixture sits inside a `display:none`
    # ancestor (the button is not itself display:none -- its wrapping div
    # is, which is what proves the ancestor walk and not merely a check of
    # the element's own style). Filtering on the field under test and
    # asserting the count is 1 is the discriminating claim: the detector
    # fires on that one case and on NOTHING ELSE in a 14-record fixture.
    invisible = [r for r in expanded if r["visible"] is False]
    assert len(invisible) == 1, expanded

    # THE CONTROL: an ordinary, rendered control in the same fixture must
    # read visible True, or this check would be trivially satisfied by a
    # detector that always reports False.
    assert expanded[0]["visible"] is True


# ---------------------------------------------------------------------------
# Classes: the shape rule and the six-token cap
# ---------------------------------------------------------------------------


async def test_classes_are_shape_filtered_and_capped_at_six():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    record = None
    for candidate in result["expanded"]["records"]:
        if "alpha-cls" in candidate["classes"]:
            record = candidate
            break
    assert record is not None
    assert record["classes"] == [
        "alpha-cls", "beta-cls", "gamma-cls", "delta-cls", "epsilon-cls",
        "zeta-cls",
    ]
    # "eta-cls" is shape-valid too -- excluded only by the six-token cap.
    assert "eta-cls" not in record["classes"]
    # A digit-run token and a too-short token are excluded by SHAPE, not cap.
    assert "bad999999" not in record["classes"]
    assert "zz" not in record["classes"]


# ---------------------------------------------------------------------------
# The select's own option terms
# ---------------------------------------------------------------------------


async def test_select_reports_option_count_and_classified_option_terms():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    selects = [r for r in result["expanded"]["records"] if r["tag"] == "select"]
    assert len(selects) == 1, result["expanded"]["records"]
    record = selects[0]
    assert record["option_count"] == 2
    assert len(record["option_terms"]) == 2
    for opt_term in record["option_terms"]:
        assert "term" not in opt_term or opt_term["term"] in probe.VOCABULARY
        if "term" not in opt_term:
            assert opt_term["refused"] in probe.REFUSAL_KEYS


# ---------------------------------------------------------------------------
# The page-level counts and the two attribute-value vocabularies
# ---------------------------------------------------------------------------


async def test_page_level_counts_and_attribute_vocabularies():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    counts = result["page_counts"]
    assert counts["aria_expanded"] == 14
    assert counts["aria_haspopup"] == 6
    assert counts["form"] == 1
    assert counts["select"] == 1
    assert counts["main_present"] is True
    assert counts["item_containers"] == 2

    expanded = result["expanded"]["records"]
    haspopup = result["haspopup"]["records"]
    # aria-expanded="mixed" is neither true nor false -> "other".
    assert expanded[2]["expanded"] == "other"
    assert expanded[0]["expanded"] == "false"
    assert expanded[1]["expanded"] == "true"
    # aria-haspopup="weird" is off the closed vocabulary -> "other".
    assert haspopup[5]["haspopup"] == "other"
    assert haspopup[0]["haspopup"] == "menu"


# ---------------------------------------------------------------------------
# The module's own declared alphabet is exactly what the fixture proves it
# can emit -- checked against `emitted_alphabet()` rather than trusted.
# ---------------------------------------------------------------------------


async def test_emitted_alphabet_covers_every_term_seen():
    probe, result, _pw_e, _pw_h = await _read_fixture()
    alphabet = probe.emitted_alphabet()
    for shape_key in ("expanded", "haspopup"):
        for record in result[shape_key]["records"]:
            term = record["term"]
            key = term.get("term") or term.get("refused")
            assert key in alphabet, (shape_key, record["idx"], term)


# ---------------------------------------------------------------------------
# The ARIA feed marker: article / [role=article], counted beside [data-urn]
# ---------------------------------------------------------------------------

ARTICLE_HTML = """
<!DOCTYPE html>
<html><body>
<header><button aria-expanded="false">Me</button></header>
<main>
  <article>
    <button aria-expanded="false" aria-label="%(menu)s">A</button>
  </article>
  <div role="article">
    <button aria-expanded="false">Comments</button>
  </div>
  <button aria-expanded="false">Loose</button>
</main>
</body></html>
""" % {"menu": LABEL_POST_CONTROL_MENU}


async def test_an_article_container_is_an_item_even_without_data_urn():
    """A feed that marks its posts only the ARIA way must not read as a page
    whose every control belongs to no post."""
    playwright = pytest.importorskip("playwright.async_api")
    probe = _probe_module()
    async with playwright.async_playwright() as pw:
        engine = await pw.chromium.launch(headless=True)
        try:
            tab = await engine.new_page()
            await tab.set_content(ARTICLE_HTML, wait_until="domcontentloaded",
                                  timeout=60_000)
            result = await tab.evaluate(probe.DISCLOSURE_TARGETS_JS, probe._build_cfg())
        finally:
            await engine.close()
    expanded = result["expanded"]["records"]
    assert [r["article_ordinal"] for r in expanded] == [-1, 0, 1, -1], expanded
    assert [r["item_ordinal"] for r in expanded] == [-1, -1, -1, -1], expanded
    assert result["page_counts"]["articles"] == 2, result["page_counts"]
    assert expanded[1]["term"] == {"term": "post_control_menu"}, expanded[1]
    assert expanded[2]["term"] == {"term": "comments"}, expanded[2]
    assert SYNTH_PERSON_A not in json.dumps(result)


# ---------------------------------------------------------------------------
# SHOWN FAILING: three defects, planted one at a time in the probe's own
# source, each caught, the file restored byte-for-byte between attempts.
#
# This is a MANUAL VERIFICATION PROCEDURE the implementer ran once while
# building this file (recorded in the wave's report with the sha256 of the
# file before and after each plant, and which assertions went red for each
# defect) rather than a permanent fixture here -- planting a defect in
# `scripts/_probe_disclosure_targets.py` and leaving it there, even
# temporarily inside a test run, is exactly the kind of edit that must never
# survive to a commit, so it is not encoded as code that mutates that file
# from inside the suite.
# ---------------------------------------------------------------------------
