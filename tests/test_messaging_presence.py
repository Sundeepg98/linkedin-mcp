"""Messaging presence -- census ``M M53``, read off a capture's skeleton.

THE ROW. "See a member's messaging presence: reachable or offline", drawn on
the composer's suggested recipients (captured 2026-09-20). The empty composer
opens no conversation; ``presence.read_suggested_presence`` reads the
suggestions and ``linkedin_messaging_presence`` returns them.

THE PEOPLE IN IT are named, so each is a people record under NAMES-AT-RUNTIME
and PEOPLE-DATA-MITIGATIONS; presence sits BESIDE the record, one of three
words this module declares. Section 3 holds the six mitigations, each with a
control that shows the check can fail.

THE FIXTURE is ``tests/fixtures/synthetic/compose_suggestions.html``, built by
``scripts/_build_capture_skeleton.py --plan suggested``: four of the
capture's seventeen cards (offline, a group, reachable, online), the
structure the capture's (the digest below is the builder's), every person
from the declared synthetic tables.
"""
from __future__ import annotations

import asyncio
import ast
import sys
from pathlib import Path

import pytest

from linkedin_server import people_data, presence
from linkedin_server import server as server_module
from tests import xhtml_page
from tests.test_people_search_names import (
    containers_written_at_module_level,
    page_calls_outside_the_allowlist,
    write_tools_reaching_through_helpers,
    _WriteSpy,
)

REPO = Path(__file__).resolve().parent.parent
FIXTURE = xhtml_page.SYNTHETIC / "compose_suggestions.html"
READER_SOURCE = REPO / "linkedin_server" / "presence.py"
SERVER_SOURCE = REPO / "linkedin_server" / "server.py"

#: Printed by the builder from the CAPTURE's kept subtree on 2026-09-28.
STRUCTURE_DIGEST = "cjlpgbpemgfecani"

PEOPLE = (
    ("Farhan Qureshi", "Engineering Manager at Umbrella Systems", "offline"),
    ("Anita Krishnan", "Principal Engineer at Umbrella Systems | Distributed Systems", "reachable"),
    ("Daniel Okonkwo", "Staff Software Engineer | Payments | Example Labs", "online"),
)

_CARDS = "document.querySelectorAll('[data-view-name=\"messaging-type-ahead-card\"]')"
_LACED_NAME = "Farhan\u200b Qureshi\u202e"
_LACE = f"() => {{ {_CARDS}[0].querySelector('dt').textContent = 'Farhan\\u200b Qureshi\\u202e'; }}"


def _builder():
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_capture_skeleton as builder  # noqa: PLC0415
    return builder


def _read(mutate: str = "") -> dict:
    return xhtml_page.read(FIXTURE, presence.read_suggested_presence, mutate=mutate)


def _rows(result: dict) -> list[tuple]:
    return [(r["person"]["name"], r["person"]["headline"], r["presence"])
            for r in result["suggested"]]


# ---------------------------------------------------------------------------
# 0. The fixture is the capture's structure, and synthetic
# ---------------------------------------------------------------------------


def test_the_fixture_carries_the_structure_the_builder_printed_from_the_capture():
    builder = _builder()
    tree = builder.Tree()
    tree.feed(FIXTURE.read_text(encoding="ascii"))
    assert builder.structure_digest(builder.SUGGESTED.select(tree.root), False) == STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_the_digest_moves_when_a_card_goes():
    builder = _builder()
    text = FIXTURE.read_text(encoding="ascii")
    start = text.index("<div><div><li")
    end = text.index("</li></div></div>", start) + len("</li></div></div>")
    tree = builder.Tree()
    tree.feed(text[:start] + text[end:])
    assert builder.structure_digest(builder.SUGGESTED.select(tree.root), False) != STRUCTURE_DIGEST


# ---------------------------------------------------------------------------
# 1. The reader over the fixture
# ---------------------------------------------------------------------------


def test_each_suggested_person_comes_back_with_the_presence_drawn():
    result = _read()
    assert _rows(result) == list(PEOPLE)
    assert result["denominators"] == {
        "cards_seen": 4, "people_returned": 3, "people_unparsed": 0,
        "groups_skipped": 1, "hidden_skipped": 0,
    }


def test_each_presence_word_is_this_module_s_own_string_not_the_page_s():
    """Equal in value is not enough: the word that leaves is the module's own
    object, so nothing the page built crosses in it."""
    for row in _read()["suggested"]:
        assert any(row["presence"] is word for word in presence.PRESENCE_WORDS), row


def test_a_group_conversation_is_counted_and_never_a_person():
    result = _read()
    assert not xhtml_page.anywhere("Example Group", result)
    assert not xhtml_page.anywhere("Group Message", result)


def test_a_card_with_no_presence_line_is_null_not_offline():
    mutate = f"() => {{ {_CARDS}[2].querySelector('span').remove(); }}"
    assert _rows(_read(mutate))[1] == (PEOPLE[1][0], PEOPLE[1][1], None)


def test_a_presence_word_outside_the_three_is_null():
    mutate = f"() => {{ {_CARDS}[0].querySelector('span').textContent = 'Status is Zzqpresenceplant'; }}"
    result = _read(mutate)
    assert _rows(result)[0][2] is None
    assert not xhtml_page.anywhere("Zzqpresenceplant", result)


def test_a_status_line_that_names_the_member_still_yields_only_the_word():
    """An earlier capture's status line carried the member's name after the
    word; only the word crosses."""
    mutate = (f"() => {{ {_CARDS}[0].querySelector('span').textContent ="
              " 'Status is offline Zzqstatusplant Markersurname'; }")
    result = _read(mutate)
    assert _rows(result)[0][2] == "offline"
    assert not xhtml_page.anywhere("Zzqstatusplant", result)


def test_the_photo_alt_is_never_read():
    mutate = (f"() => {{ {_CARDS}[0].querySelector('img')"
              ".setAttribute('alt', 'Suggested: Photo of Zzqaltplant Markersurname'); }")
    assert not xhtml_page.anywhere("Zzqaltplant", _read(mutate))


def test_the_tool_returns_the_suggestions_off_one_load_of_the_empty_composer():
    envelope = xhtml_page.drive_tool(FIXTURE, server_module.linkedin_messaging_presence)
    assert envelope["ok"] is True and envelope["pages_loaded"] == 1
    assert envelope["_gotos"] == [server_module.CENSUS_SURFACES["messaging_compose"]]
    assert _rows(envelope) == list(PEOPLE)


# ---------------------------------------------------------------------------
# 3. The six mitigations, each with a control that can fail
# ---------------------------------------------------------------------------


def test_mitigation_1_declared_fields_only():
    for row in _read()["suggested"]:
        assert set(row) == {"person", "presence"}
        assert set(row["person"]) == people_data.PERSON_SHAPE
        assert row["presence"] in presence.PRESENCE_WORDS + (None,)


def test_mitigation_2_sanitised_and_marked_untrusted():
    row = _read(_LACE)["suggested"][0]
    assert row["person"]["name"] == people_data.sanitise(_LACED_NAME, cap=120)
    assert "\u200b" not in row["person"]["name"] and "\u202e" not in row["person"]["name"]
    assert row["person"][people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE


def test_THIS_CONTROL_CAN_FAIL_the_laced_name_reaches_the_page():
    async def raw(page):
        return await page.evaluate(f"() => {_CARDS}[0].querySelector('dt').textContent")
    assert "\u200b" in xhtml_page.read(FIXTURE, raw, mutate=_LACE)


def test_mitigation_3_never_stored_no_state_no_file_no_log(monkeypatch):
    source = READER_SOURCE.read_text(encoding="utf-8")
    assert containers_written_at_module_level(source) == []
    assert "logging" not in source and "print(" not in source
    spy = _WriteSpy(monkeypatch)

    async def action(page):
        spy.armed = True
        try:
            return await presence.read_suggested_presence(page)
        finally:
            spy.armed = False

    assert len(asyncio.run(xhtml_page.with_page(FIXTURE, action))["suggested"]) == 3
    assert spy.opened == []


def test_mitigation_4_one_page_per_call_nothing_but_finding_and_reading():
    envelope = xhtml_page.drive_tool(FIXTURE, server_module.linkedin_messaging_presence)
    assert len(envelope["_gotos"]) == 1
    assert page_calls_outside_the_allowlist(READER_SOURCE.read_text(encoding="utf-8")) == []


def test_THIS_CONTROL_CAN_FAIL_a_hover_in_the_reader_is_refused():
    anchor = "            seen += 1" + chr(10)
    source = READER_SOURCE.read_text(encoding="utf-8")
    assert source.count(anchor) == 1
    planted = source.replace(anchor, anchor + "            await card.hover()" + chr(10))
    assert page_calls_outside_the_allowlist(planted) != []


def test_mitigation_5_visible_only_a_hidden_card_is_counted_and_not_read():
    result = _read(f"() => {{ {_CARDS}[2].style.display = 'none'; }}")
    assert [r[0] for r in _rows(result)] == [PEOPLE[0][0], PEOPLE[2][0]]
    assert result["denominators"]["hidden_skipped"] == 1


def test_mitigation_5_a_list_hidden_from_assistive_technology_is_not_read():
    result = _read("() => { document.querySelector('[aria-hidden]')"
                   ".setAttribute('aria-hidden', 'true'); }")
    assert result["suggested"] == []
    assert result["denominators"]["hidden_skipped"] == 4


def test_THIS_CONTROL_CAN_FAIL_the_list_container_is_the_one_the_capture_marked_shown():
    async def flag(page):
        return await page.evaluate("() => document.querySelector('[aria-hidden]').getAttribute('aria-hidden')")
    assert xhtml_page.read(FIXTURE, flag) == "false"


def test_mitigation_6_never_a_target_no_link_and_no_write_reaches_the_reader():
    assert all(r["person"]["link"] is None for r in _read()["suggested"])
    assert write_tools_reaching_through_helpers(
        SERVER_SOURCE.read_text(encoding="utf-8"), "presence") == []


def test_the_tool_is_a_declared_people_tool():
    assert "linkedin_messaging_presence" in people_data.PEOPLE_TOOLS


def test_a_failing_page_raises_by_type_alone():
    class Failing:
        async def query_selector_all(self, *args, **kwargs):
            raise ValueError("Zzqfailureplant Markersurname")

    with pytest.raises(RuntimeError) as caught:
        asyncio.run(presence.read_suggested_presence(Failing()))
    assert "Zzqfailureplant" not in str(caught.value)
    assert caught.value.__cause__ is None and caught.value.__suppress_context__
