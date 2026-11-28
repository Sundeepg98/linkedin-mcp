"""What a press did to the page, as the live runner judges it: the panel rule's evidence, a region's
digest, the words a press may never aim at, and where a self-root press landed.

WHY THIS FILE EXISTS. Session 14b's runner lives in gitignored state, and its red-first checks
(``close_checks_s14b.py`` K3, ``gate_checks_s14b.py`` Q6, Q7, R4 and R6) ran only on the operator's
machine. What those checks test is pure: two read-only JS functions that count the form controls a
press added, a JS digest of a region, two word sets, and ``press_landing``. Lane ci-checks28 tracked
them VERBATIM in ``scripts/live_runner_rules.py``. These are the live checks' own cases, under the
same names.

THE PANEL RULE'S EVIDENCE, AND ONLY ITS EVIDENCE. The live K3 checks press a trigger, and then the
runner's ``close_all`` closes what it opened, or stops. That close path is page code in the gitignored
runner, and it stays local. What moves is the question the close path asks first: did the press ADD
form controls? The pages are session 14's own TRACKED skeletons (``tests/fixtures/live12``, ``live13``
and ``live14``). Each model's mutation is the live check's own, made at once rather than on a 50 ms
timer: no wait, real or scaled. Every request a skeleton makes is aborted by this file's own route,
before the network guard could see it.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import live_runner_rules as rules  # noqa: E402

FIX = REPO / "tests" / "fixtures"

#: The live check's own models (close_checks_s14b.py MODEL_PANEL_JS), minus the trigger button and
#: the 50 ms timer: the mutation each press made, made at once, between the two readings.
MODEL_JS = r"""
([mode, afterHtml]) => {
  // Returns {setup, moved}: "ok", and how many controls the model put on the page (or re-rendered).
  const host = document.querySelector("main section") || document.querySelector("main");
  if (!host) return {setup: "no section of main in the skeleton", moved: 0};
  const SEL = 'input[type=checkbox], input[type=radio], [role=checkbox], [role=radio], [role=switch], select, input[type=range]';
  const total = () => document.querySelectorAll(SEL).length;
  const was = total();
  const boxes = (n, into) => { for (let i = 0; i < n; i++) { const l = document.createElement("label");
      const c = document.createElement("input"); c.type = "checkbox"; l.append(c, document.createTextNode("Option " + i));
      into.append(l); } };
  // the REAL controls session 14's photo press saw: the after skeleton's checkboxes, with or
  // without the sections that hold them
  const realSections = () => {
    const doc = new DOMParser().parseFromString(afterHtml, "text/html");
    const secs = new Set();
    for (const c of doc.querySelectorAll("main section input[type=checkbox]")) secs.add(c.closest("main section"));
    return Array.from(secs);
  };
  if (mode === "late_render") {
    // the page rendering on: a NEW nested section of main gains checkboxes
    const inner = document.createElement("section");
    host.append(inner);
    boxes(5, inner);
  } else if (mode === "photo_replay") {
    // session 14's photo press: the sections holding the after skeleton's checkboxes arrive as NEW
    // sections of main
    const secs = realSections();
    if (!secs.length) return {setup: "the after skeleton draws no checkbox in a section of main", moved: 0};
    for (const s of secs) host.append(document.adoptNode(s));
  } else if (mode === "photo_inline_replay") {
    // the same real checkboxes, revealed INSIDE the existing section (an inline panel)
    for (const s of realSections())
      for (const c of Array.from(s.querySelectorAll("input[type=checkbox]"))) {
        const l = c.closest("label") || c; host.append(document.adoptNode(l)); }
  } else if (mode === "redraw") {
    // round 2's MINOR-A: the press REDRAWS an existing section of main -- a new element, the count
    // unchanged -- and draws a panel inside it
    const secs = Array.from(document.querySelectorAll("main section"))
      .filter((x) => x !== host && !x.contains(host) && !host.contains(x));
    if (!secs.length) return {setup: "no second section of main to redraw", moved: 0};
    const old = secs[0];
    const nu = old.cloneNode(true);
    const p = document.createElement("div");
    boxes(3, p);
    nu.append(p);
    old.replaceWith(nu);
  } else if (mode === "inline") {
    // round 1's K3x: a Filters-like control reveals checkboxes inside the SAME existing section
    const p = document.createElement("div");
    boxes(3, p);
    host.append(p);
  } else if (mode === "aside") {
    // a real panel's shape: drawn in an aside outside main, as the three All filters panels were
    const a = document.createElement("aside");
    boxes(3, a);
    document.body.append(a);
  } else if (mode === "rerender") {
    // session 13's rule F: a page re-rendering its OWN controls adds none
    const all = Array.from(document.querySelectorAll("input[type=checkbox]"));
    for (const c of all) c.replaceWith(c.cloneNode(true));
    return {setup: "ok", moved: all.length};
  } else {
    return {setup: "unknown mode", moved: 0};
  }
  return {setup: "ok", moved: total() - was};
}
"""

#: The live check's SWAP_JS: the document replaced in the same realm, for a real pair of
#: skeletons (every section is then a new element: used only for panels drawn OUTSIDE main).
SWAP_JS = r"""
(html) => {
  const doc = new DOMParser().parseFromString(html, "text/html");
  document.replaceChild(document.adoptNode(doc.documentElement), document.documentElement);
  return document.querySelectorAll("input").length;
}
"""

#: Session 12's and 13's real All filters panels, before and after their press.
REAL_PANELS = {
    "live13 jobs All filters": ("live13/c_srch_3a.html", "live13/c_srch_3a_all_filters-open.html"),
    "live12 content All filters": ("live12/search_content.html", "live12/search_content_all_filters-open.html"),
    "live12 people All filters": ("live12/search_people_first_degree.html",
                                  "live12/search_people_all_filters-open.html"),
}
MODES = ("late_render", "photo_replay", "photo_inline_replay", "redraw", "inline", "aside", "rerender")

REGION_Q6 = ("<main><section id='reg'><select id='s'><option>aa</option><option>bb</option></select>"
             "<input id='t' value='abc'></section></main>")
REGION_R4 = ("<main><section id='reg'><div id='sw' role='switch' aria-checked='true' "
             "aria-label='Manage alert notifications'>x</div><button id='ok' aria-label='Edit alert'>x</button>"
             "<input id='cb' type='checkbox' checked></section><p id='outside'>elsewhere</p></main>")


def _read(name: str) -> str:
    return (FIX / name).read_text(encoding="ascii")


async def _measure() -> dict:
    """Every page reading this file asserts on, in ONE local headless Chromium."""
    from playwright.async_api import async_playwright

    out: dict = {"models": {}, "real": {}, "digest": {}}
    more, photo = _read("live14/in_me_more-open.html"), _read("live14/in_me_photo-open.html")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            ctx = await browser.new_context()
            await ctx.route("**/*", lambda route: route.abort())
            pg = await ctx.new_page()
            for mode in MODES:
                await pg.set_content(more, wait_until="domcontentloaded")
                before = await pg.evaluate_handle(rules.FORM_SIGS_JS)
                setup = await pg.evaluate(MODEL_JS, [mode, photo])
                delta = await pg.evaluate(rules.FORM_DELTA_JS, before)
                await before.dispose()
                out["models"][mode] = dict(delta or {}, setup=setup["setup"], moved=setup["moved"])
            for label, (before_name, after_name) in REAL_PANELS.items():
                await pg.set_content(_read(before_name), wait_until="domcontentloaded")
                before = await pg.evaluate_handle(rules.FORM_SIGS_JS)
                await pg.evaluate(SWAP_JS, _read(after_name))
                out["real"][label] = await pg.evaluate(rules.FORM_DELTA_JS, before) or {}
                await before.dispose()

            async def digest() -> str:
                return await (await pg.query_selector("#reg")).evaluate(rules.SECTION_DIGEST_JS)

            await pg.set_content(REGION_Q6)
            q6 = [await digest()]
            await pg.evaluate("() => { document.getElementById('s').selectedIndex = 1; }")
            q6.append(await digest())
            await pg.evaluate("() => { document.getElementById('t').value = 'xyz'; }")
            q6.append(await digest())
            out["digest"]["q6"] = q6
            await pg.set_content(REGION_R4)
            r4 = [await digest(), await digest()]
            await pg.evaluate("() => { document.getElementById('outside').textContent = 'moved'; }")
            r4.append(await digest())
            await pg.evaluate("() => { document.getElementById('cb').checked = false; }")
            r4.append(await digest())
            out["digest"]["r4"] = r4
        finally:
            await browser.close()
    return out


@pytest.fixture(scope="module")
def measured() -> dict:
    return asyncio.run(_measure())


def model(measured: dict, mode: str) -> dict:
    got = measured["models"][mode]
    assert got["setup"] == "ok", (mode, got["setup"])
    assert got["moved"] > 0, (mode, "the model put nothing on the page, so nothing is tested")
    return got


def counted_apart(got: dict) -> int:
    """Controls the rule SAW but counted apart as the page rendering on. A rule that has no such
    count (session 14's, 14b r1's) counts none apart, so a missing field reads 0 here; the two tests
    that assert a positive number are what make the field required."""
    return int(got.get("in_new_sections", 0))


# ---------------------------------------------------------------------------------------------
# The panel rule's evidence (close_checks_s14b.py K3). Each live check judged the close the
# evidence led to; each test here asserts the evidence that close rests on: ``added`` > 0 is a
# panel to close (closed by Escape, or did_not_close), and ``added`` == 0 is nothing_opened.
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize("label", sorted(REAL_PANELS), ids=lambda label: label.replace(" ", "-"))
def test_k3b_control_the_three_real_panels_still_count_as_opened(measured, label) -> None:
    """Session 12's and 13's All filters panels, drawn in an aside outside main: real evidence."""
    assert int(measured["real"][label].get("added") or 0) > 0, measured["real"][label]


def test_k3a_the_photo_press_replayed_adds_nothing_its_controls_are_in_new_sections(measured) -> None:
    """Session 14's photo press: its REAL checkboxes arrived in sections of main drawn after the
    press. That is the page rendering on, not a panel, so nothing is left to close."""
    got = model(measured, "photo_replay")
    assert got["added"] == 0, got


def test_k3c_a_new_section_of_main_gaining_controls_is_the_page_rendering_on(measured) -> None:
    got = model(measured, "late_render")
    assert got["added"] == 0, got


def test_k3_the_controls_of_a_late_render_are_counted_apart_never_lost(measured) -> None:
    """14b r1b's K3: a control in a section drawn after the press is SEEN and counted apart, every
    one of them, so a record can say what rendered."""
    for mode in ("photo_replay", "late_render"):
        got = model(measured, mode)
        assert counted_apart(got) == got["moved"], (mode, got)


def test_k3z_the_photos_real_checkboxes_revealed_in_place_are_a_panel(measured) -> None:
    """Round 1's MINOR-1: the same real controls inside an EXISTING section are evidence, every one."""
    got = model(measured, "photo_inline_replay")
    assert got["added"] == got["moved"], got


def test_k3x_k3y_controls_revealed_inside_an_existing_section_are_a_panel(measured) -> None:
    """The evidence K3x (closed by Escape) and K3y (did_not_close) both rest on."""
    got = model(measured, "inline")
    assert (got["added"], got["kinds"]) == (got["moved"], {"checkbox": got["moved"]}), got


def test_k3w_k3v_a_panel_drawn_in_a_section_the_press_redraws_is_a_panel(measured) -> None:
    """Round 2's MINOR-A: a redrawn section is a new element, but main's sections did not GROW, so
    a panel drawn inside it stays evidence."""
    got = model(measured, "redraw")
    assert got["added"] == got["moved"], got


def test_k3d_k3e_control_a_panel_in_an_aside_outside_main_is_a_panel(measured) -> None:
    got = model(measured, "aside")
    assert got["added"] == got["moved"], got


def test_no_control_in_a_section_that_existed_is_counted_apart(measured) -> None:
    for mode in ("photo_inline_replay", "inline", "redraw", "aside", "rerender"):
        assert counted_apart(model(measured, mode)) == 0, (mode, measured["models"][mode])


def test_control_a_page_re_rendering_its_own_controls_adds_none(measured) -> None:
    """Session 13's rule F, the reason the evidence is a multiset of signatures."""
    got = model(measured, "rerender")
    assert got["added"] == 0, got


# ---------------------------------------------------------------------------------------------
# A region's digest (gate_checks_s14b.py Q6, and R4's digest half)
# ---------------------------------------------------------------------------------------------


def test_q6_a_select_moved_and_a_text_value_replaced_each_of_equal_length_change_the_digest(measured) -> None:
    """MINOR-C: the value itself and a select's index are digested, so a change that keeps every
    length still changes the digest."""
    d0, d1, d2 = measured["digest"]["q6"]
    assert all(re.fullmatch(r"[0-9a-f]{8}", d) for d in (d0, d1, d2)), (d0, d1, d2)
    assert d0 != d1 and d1 != d2, (d0, d1, d2)


def test_r4_a_flipped_checkbox_changes_the_regions_digest(measured) -> None:
    """MAJOR-4: the region's CONTROL STATES are digested with its text, so a toggle's flip is a
    change. Its control: the same region digests the same twice, and a change OUTSIDE it is not
    its change."""
    first, again, outside_moved, flipped = measured["digest"]["r4"]
    assert first == again == outside_moved, (first, again, outside_moved)
    assert flipped != first, (first, flipped)


# ---------------------------------------------------------------------------------------------
# The words (gate_checks_s14b.py R6)
# ---------------------------------------------------------------------------------------------


def test_r6_no_panel_close_word_is_one_publish_words_forbids() -> None:
    """MINOR-4: Done is a publishing word, so a panel is never closed by pressing Done."""
    assert rules.PANEL_CLOSE_WORDS, "an empty close vocabulary passes vacuously"
    assert not set(rules.PANEL_CLOSE_WORDS) & set(rules.PUBLISH_WORDS), (
        sorted(set(rules.PANEL_CLOSE_WORDS) & set(rules.PUBLISH_WORDS)))
    assert {"Done", "Save", "Send", "Post", "Delete"} <= set(rules.PUBLISH_WORDS)


# ---------------------------------------------------------------------------------------------
# Where a self-root press landed (gate_checks_s14b.py Q7, the cold review's MAJOR-1)
# ---------------------------------------------------------------------------------------------

#: The owner's slug, synthetic: a value tests/test_a_person_name_is_never_a_literal.py declares invented.
MEMBER = "someone-example-1"
M = "https://www.linkedin.com/in/" + MEMBER + "/"
ROOT = "/in/" + MEMBER + "/"
POSITION = M + "edit/forms/position/new/?profileFormEntryPoint=identityModuleMirror"


def landed(now_url: str, loaded: bool = True, raw: str = POSITION) -> str:
    return rules.press_landing(now_url, raw, MEMBER, ROOT, loaded)


def test_q7_an_added_tracking_key_is_no_veto_and_the_targets_own_key_with_another_value_is() -> None:
    """NIT-A: each of the target's OWN parameters must be there with exactly its value; a key
    LinkedIn adds on landing is not a veto."""
    assert landed(POSITION + "&trk=synthetic") == "target"
    assert landed(POSITION.replace("identityModuleMirror", "other")) == "not_its_target"
    assert landed(POSITION.split("?")[0]) == "not_its_target", "the target's own key is missing"


def test_an_in_page_opening_is_judged_by_its_path_alone() -> None:
    assert landed(POSITION.split("?")[0], loaded=False) == "target"


def test_the_alias_form_of_the_target_is_the_target() -> None:
    alias = POSITION.replace("/in/" + MEMBER + "/", "/in/me/")
    assert landed(alias) == "target"
    assert rules.press_landing(POSITION, alias, MEMBER, ROOT, True) == "target"


def test_his_root_is_named_as_his_root() -> None:
    for now in (M, "https://www.linkedin.com/in/me/"):
        assert landed(now) == "his_root", now


@pytest.mark.parametrize("now", [
    POSITION.replace("https://", "http://"),
    POSITION.replace("www.linkedin.com", "linkedin.com"),
    POSITION + "#fragment",
    "https://www.linkedin.com/in/someone-else/edit/forms/position/new/"
    "?profileFormEntryPoint=identityModuleMirror",
    "https://www.linkedin.com/feed/",
    "",
    "http://[",
], ids=["http", "bare-host", "fragment", "another-member", "feed", "empty", "unparsable"])
def test_anywhere_else_is_not_its_target(now) -> None:
    assert landed(now) == "not_its_target"
