"""The profile-engagement cards -- census ``P S5``, read off a capture's skeleton.

THE ROW. "Profile engagement insights: impressions on one experience entry,
and recent clicks on a profile section", drawn on /analytics/search-appearances/
as two cards (captured 2026-09-20). ``linkedin_search_appearances`` already
loads that page, and ``dom.read_search_appearances`` now reads the cards off
the same render, in the same script, returning them as ``engagement``.

THE CENSUS CELL'S CONDITION, HELD HERE: "the company the first names is an
employer, which a reader must not publish". The script's pattern stops at
"at", so the employer never leaves the page; section 3 hunts it everywhere the
reader and the tool can put anything.

THE FIXTURE is ``tests/fixtures/synthetic/search_appearances_engagement.html``,
built from the capture by ``scripts/_build_capture_skeleton.py --plan
engagement``: its structure is the capture's (the digest in section 0 is the
one the builder printed from the capture), its employer and number invented.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from linkedin_server import dom
from linkedin_server import server as server_module
from tests import xhtml_page
from tests.plantedpage import PLANT, PageString

REPO = Path(__file__).resolve().parent.parent
FIXTURE = xhtml_page.SYNTHETIC / "search_appearances_engagement.html"

#: Printed by the builder from the CAPTURE's kept subtree on 2026-09-28.
STRUCTURE_DIGEST = "bffkmckmmpfkjjff"

#: The invented employer the fixture's first card names.
EMPLOYER = "Umbrella Systems"


def _builder():
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_capture_skeleton as builder  # noqa: PLC0415
    return builder


def _read(mutate: str = "") -> dict:
    return xhtml_page.read(FIXTURE, dom.read_search_appearances, mutate=mutate)["engagement"]


def _card_text(old: str, new: str) -> str:
    """A page drawing: the card text node ending ``old`` is rewritten to ``new``."""
    return ("() => { for (const d of document.querySelectorAll('div')) {"
            f" if (d.children.length === 0 && d.textContent.includes({old!r}))"
            f" d.textContent = {new!r}; }} }}")


# ---------------------------------------------------------------------------
# 0. The fixture is the capture's structure, and synthetic
# ---------------------------------------------------------------------------


def test_the_fixture_carries_the_structure_the_builder_printed_from_the_capture():
    builder = _builder()
    tree = builder.Tree()
    tree.feed(FIXTURE.read_text(encoding="ascii"))
    assert builder.structure_digest(builder.ENGAGEMENT.select(tree.root), False) == STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_the_digest_moves_when_an_attribute_does():
    """The attributes the reader selects on are in the digest: a button that
    is no longer a button fails it."""
    builder = _builder()
    tree = builder.Tree()
    tree.feed(FIXTURE.read_text(encoding="ascii").replace('type="button"', 'type="submit"', 1))
    assert builder.structure_digest(builder.ENGAGEMENT.select(tree.root), False) != STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_the_digest_moves_when_the_structure_does():
    builder = _builder()
    tree = builder.Tree()
    tree.feed(FIXTURE.read_text(encoding="ascii").replace("<span>View</span>", "View", 1))
    assert builder.structure_digest(builder.ENGAGEMENT.select(tree.root), False) != STRUCTURE_DIGEST


# ---------------------------------------------------------------------------
# 1. The reader over the fixture
# ---------------------------------------------------------------------------


def test_both_cards_are_read_and_nothing_else_comes_back():
    assert _read() == {
        "experience_impressions": [7],
        "section_clicks": [{"section": "intro", "actor": "someone"}],
        "cards_drawn": 2,
        "cards_seen": 2,
        "cards_unreadable": 0,
        "unrecognised_sections": 0,
    }


def test_a_thousands_comma_is_read_as_a_number():
    mutate = _card_text("You have 7", "You have 1,204 impressions on your experience at Umbrella Systems")
    assert _read(mutate)["experience_impressions"] == [1204]


def test_a_section_outside_the_closed_list_is_counted_and_never_returned():
    result = _read(_card_text("your Intro", "Someone recently clicked on your Zzqsectionplant"))
    assert result["section_clicks"] == [{"section": None, "actor": "someone"}]
    assert result["unrecognised_sections"] == 1
    assert not xhtml_page.anywhere("zzqsectionplant", str(result).lower())


def test_a_click_by_a_named_member_says_so_and_never_names_them():
    result = _read(_card_text("your Intro", "Zzqactorplant Markersurname recently clicked on your Intro"))
    assert result["section_clicks"] == [{"section": "intro", "actor": "other"}]
    assert not xhtml_page.anywhere("Zzqactorplant", result)


def test_a_hidden_card_is_not_read():
    mutate = "() => { document.querySelectorAll('li button')[1].style.display = 'none'; }"
    result = _read(mutate)
    assert result["section_clicks"] == [] and result["cards_seen"] == 1
    assert result["cards_drawn"] == 1


def test_a_page_without_the_cards_reads_as_none_seen():
    result = _read("() => { document.querySelector('ul').remove(); }")
    assert result["cards_seen"] == 0 and result["cards_drawn"] == 0
    assert result["experience_impressions"] == [] and result["section_clicks"] == []


def test_a_card_in_a_shape_the_patterns_do_not_know_is_drawn_not_absent():
    """A compact count is not guessed at: the card is DRAWN and not read, so
    the reading says so instead of reporting no card."""
    result = _read(_card_text("You have 7", "You have 1.2K impressions on your experience at Umbrella Systems"))
    assert result["experience_impressions"] == []
    assert result["cards_drawn"] == 2 and result["cards_seen"] == 1


def test_a_multi_word_section_is_counted_unrecognised_not_dropped():
    result = _read(_card_text("your Intro", "Someone recently clicked on your Licenses & certifications"))
    assert result["section_clicks"] == [{"section": None, "actor": "someone"}]
    assert result["unrecognised_sections"] == 1 and result["cards_seen"] == 2


# ---------------------------------------------------------------------------
# 2. The tool returns them beside the search appearances
# ---------------------------------------------------------------------------


def test_the_tool_returns_the_cards_as_engagement_off_its_one_load():
    envelope = xhtml_page.drive_tool(FIXTURE, server_module.linkedin_search_appearances)
    assert envelope["ok"] is True and envelope["pages_loaded"] == 1
    assert len(envelope["_gotos"]) == 1
    assert envelope["engagement"]["experience_impressions"] == [7]
    assert envelope["engagement"]["section_clicks"] == [{"section": "intro", "actor": "someone"}]


# ---------------------------------------------------------------------------
# 3. The employer never leaves
# ---------------------------------------------------------------------------


def test_the_employer_is_nowhere_in_the_reading_or_the_envelope():
    reading = xhtml_page.read(FIXTURE, dom.read_search_appearances)
    assert not xhtml_page.anywhere(EMPLOYER, reading)
    envelope = xhtml_page.drive_tool(FIXTURE, server_module.linkedin_search_appearances)
    assert not xhtml_page.anywhere(EMPLOYER, envelope)


def test_THIS_CONTROL_CAN_FAIL_the_employer_is_in_the_page_it_is_hunted_in():
    async def page_text(page):
        return await page.evaluate("() => document.body.innerText")
    assert EMPLOYER in xhtml_page.read(FIXTURE, page_text)


def test_the_script_captures_no_group_that_could_hold_the_employer():
    """The impressions pattern has ONE group, the number, and ends at "at "."""
    line = next(ln for ln in dom.SEARCH_APPEARANCES_JS.splitlines()
                if "const IMPRESSIONS" in ln)
    assert line.count("(") - line.count("(?") == 1, line
    assert line.rstrip().endswith("at /;"), line


def test_a_page_answering_in_text_carries_nothing_out_of_the_engagement_step():
    """``_engagement`` over values a page chose: nothing of them comes back."""
    planted = PageString(PLANT)
    for raw in (planted, {"impressions": planted, "clicks": planted,
                          "unrecognised": planted},
                {"impressions": [planted, 3], "clicks": [{"section": planted,
                                                           "someone": planted}]}):
        result = dom._engagement(raw)
        assert not xhtml_page.anywhere(PLANT, result), result
        assert result["cards_unreadable"] >= 1


def test_a_section_word_the_script_let_through_is_still_checked_here():
    """The script nulls a word outside the list; the Python step checks again,
    and what leaves is this module's own string, never the page's object."""
    result = dom._engagement({"impressions": [], "clicks": [
        {"section": PageString(PLANT), "someone": True},
        {"section": "".join(["in", "tro"]), "someone": False},
    ]})
    assert not xhtml_page.anywhere(PLANT, result), result
    assert result["section_clicks"][0] == {"section": None, "actor": "someone"}
    assert result["section_clicks"][0]["actor"] is dom.ENGAGEMENT_ACTORS[0]
    assert result["section_clicks"][1]["section"] is dom.ENGAGEMENT_SECTIONS[0]


@pytest.mark.parametrize("verb", ["click(", "scroll", "focus(", "dispatchEvent", "hover",
                                  ".value =", "submit("])
def test_the_script_presses_scrolls_and_types_nothing(verb):
    assert verb not in dom.SEARCH_APPEARANCES_JS
