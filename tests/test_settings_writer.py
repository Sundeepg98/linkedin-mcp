"""The generic settings writer's verdicts and readers (lane S, 2026-10-10).

``linkedin_server/settings_writer.py`` serves ``linkedin_set_admitted_setting``:
ONE admitted settings page, ONE control on it, by the label LinkedIn draws,
behind the single-use grant (``HIS-OWN-SETTINGS-NOT-OUTWARD``). This file holds
its PURE verdicts and its READERS; the press itself is ``writes.perform``'s,
and ``tests/test_set_admitted_setting.py`` drives that end to end.

THREE SYNTHETIC PATTERNS, THEN THE REAL PAGE. The synthetic pages model the
three kinds the writer sets -- a switch drawn as ``div[role=switch]`` with
``aria-checked``, a radio group of inputs named through ``aria-labelledby``, a
select with a Save -- and each can be told to land its press late, to ignore
it, or to move a second control too. Their names are invented. The REAL page is
``tests/fixtures/live2/setting.html``, the live lane's capture of "Share
profile updates" (2026-09-28) reduced to a skeleton, and it is the one record
the admitted registry is measured on.

WHY SCENARIOS SHARE A TEST. A browser launch and close is most of a test's
price on this box (``tests/test_leave_group.py`` measured 2.6-19 s against
under 2.3 s of body), so the scenarios of one check run in a loop over one
browser, each assertion carrying its scenario's label.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from linkedin_server import profile_editor, settings_writer as sw
from linkedin_server.errors import WriteAttemptError
from tests.test_writes import browser_page  # noqa: F401 -- fixture

_SYNTHETIC = Path(__file__).parent / "fixtures" / "synthetic"
_MARKER = "<!--FIXTURE_CONFIG-->"
_JOIN = " :: "

SWITCH_MARKUP = (_SYNTHETIC / "settings_switch_aria.html").read_text(encoding="ascii")
RADIO_MARKUP = (_SYNTHETIC / "settings_radio_group.html").read_text(encoding="ascii")
SELECT_MARKUP = (_SYNTHETIC / "settings_select.html").read_text(encoding="ascii")

#: THE REAL PAGE: the live lane's capture of "Share profile updates",
#: 2026-09-28, as a tracked skeleton (LinkedIn's words kept, other text "x").
REAL_CAPTURE = Path(__file__).parent / "fixtures" / "live2" / "setting.html"


def world(markup: str, **config) -> str:
    """The fixture with its behaviour chosen, always explicitly."""
    assert markup.count(_MARKER) == 1
    return markup.replace(
        _MARKER, f"<script>window.__fixtureConfig = {json.dumps(config)};</script>"
    )


#: The synthetic controls, described as an admitted page's records would be.
#: Invented names; the shapes are the three the writer sets.
SYN_SWITCH = sw.AdmittedControl(
    label="Synthetic alerts",
    kind=sw.SWITCH,
    values=sw.SWITCH_VALUES,
    meanings=(("on", "synthetic on"), ("off", "synthetic off")),
    visible_to_others=False,
    live_proof=sw.LIVE_PROOF_ALLOWED,
    live_proof_why="synthetic",
    rows=(),
)
SYN_RADIO = sw.AdmittedControl(
    label="Synthetic display",
    kind=sw.RADIO_GROUP,
    values=("Never", "Always", "Follow the device"),
    meanings=(),
    visible_to_others=False,
    live_proof=sw.LIVE_PROOF_ALLOWED,
    live_proof_why="synthetic",
    rows=(),
)
SYN_SELECT = sw.AdmittedControl(
    label="Synthetic language",
    kind=sw.SELECT,
    values=("Alpha", "Beta", "Gamma"),
    meanings=(),
    visible_to_others=False,
    live_proof=sw.LIVE_PROOF_ALLOWED,
    live_proof_why="synthetic",
    rows=(),
)
SYN_SELECT_PAGE = sw.AdmittedPage(
    name="Synthetic select",
    url="https://www.linkedin.com/mypreferences/d/settings/synthetic-select",
    save_label="Save",
    controls=(SYN_SELECT,),
    capture="tests/fixtures/synthetic/settings_select.html",
    admitted_by="synthetic",
)

THE_PAGE = sw.SHARE_PROFILE_UPDATES
THE_CONTROL = THE_PAGE.controls[0]


# ---------------------------------------------------------------------------
# 1. The registry: one page, admitted by name, measured on its capture
# ---------------------------------------------------------------------------


def test_one_page_is_admitted_and_it_is_the_captured_one():
    assert [p.name for p in sw.ADMITTED_PAGES] == ["Share profile updates"]
    assert THE_PAGE.url == profile_editor.ACCOUNT_SETTING_URL
    assert THE_PAGE.capture == "tests/fixtures/live2/setting.html"
    assert (Path(__file__).resolve().parents[1] / THE_PAGE.capture).is_file()
    assert [c.label for c in THE_PAGE.controls] == [profile_editor.ACCOUNT_SETTING_NAME]
    assert THE_CONTROL.kind == sw.SWITCH
    assert THE_CONTROL.live_proof in sw.LIVE_PROOF_CLASSES
    assert THE_CONTROL.rows == ("P O6-O20",)


def test_every_admitted_control_is_a_settable_kind_with_meanings_for_each_value():
    for page in sw.ADMITTED_PAGES:
        for control in page.controls:
            assert sw.check_kind(control.kind) == control.kind
            assert control.live_proof in sw.LIVE_PROOF_CLASSES, control.label
            assert {v for v, _ in control.meanings} == set(control.values), control.label
            for name in (page.name, control.label) + control.values:
                assert sw.SETTING_JOIN not in name and _JOIN not in name, name
                assert name.isascii(), name


def test_the_write_pattern_admits_the_admitted_address_and_nothing_beside_it():
    pattern = sw.url_pattern()
    assert pattern.match(THE_PAGE.url)
    assert pattern.match(THE_PAGE.url + "/")
    for other in (
        "https://www.linkedin.com/mypreferences/d/settings/language",
        "https://www.linkedin.com/mypreferences/d/settings/notify-network-for-updates-x",
        "https://www.linkedin.com/mypreferences/d/settings/notify-network-for-updates/x",
        "https://www.linkedin.com/mypreferences/d/dark-mode",
        "http://www.linkedin.com/mypreferences/d/settings/notify-network-for-updates",
    ):
        assert not pattern.match(other), other


# ---------------------------------------------------------------------------
# 2. The pure verdicts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", sorted(sw.REFUSED_KINDS) + ["slider", ""])
def test_a_kind_that_is_not_a_switch_radio_group_or_select_is_refused_by_name(kind):
    with pytest.raises(WriteAttemptError) as caught:
        sw.check_kind(kind)
    assert "refused" in str(caught.value)
    if kind in sw.REFUSED_KINDS:
        assert sw.REFUSED_KINDS[kind] in str(caught.value)


def test_the_three_kinds_are_accepted():
    assert [sw.check_kind(k) for k in ("switch", "Radio_Group", " select ")] == list(sw.CONTROL_KINDS)


def test_a_page_and_a_control_are_admitted_by_their_exact_names():
    assert sw.resolve("Share profile updates", "Share key profile updates") == (THE_PAGE, THE_CONTROL)
    assert sw.resolve("  Share  profile updates ", "Share key  profile updates") == (THE_PAGE, THE_CONTROL)
    for page_name, label, why in (
        ("share profile updates", "Share key profile updates", "not an admitted settings page"),
        ("Sharing profile edits", "Share key profile updates", "not an admitted settings page"),
        ("Dark mode", "Always on", "not an admitted settings page"),
        ("Share profile updates", "Share profile updates", "draws no admitted control"),
        ("Share profile updates", "share key profile updates", "draws no admitted control"),
    ):
        with pytest.raises(WriteAttemptError) as caught:
            sw.resolve(page_name, label)
        assert why in str(caught.value), (page_name, label)
        # Each refusal names what IS admitted: the whole surface for an
        # unadmitted page, the page's own controls for an unadmitted control.
        assert "Share key profile updates" in str(caught.value), (page_name, label)
        if why.startswith("not an admitted"):
            assert "Share profile updates / Share key profile updates" in str(caught.value)


def test_a_value_is_one_the_control_holds_spelled_its_own_way():
    assert sw.canonical_value(THE_CONTROL, "ON") == "on"
    assert sw.canonical_value(SYN_RADIO, "follow the device") == "Follow the device"
    for bad in ("maybe", "", "on, off", "Of"):
        with pytest.raises(WriteAttemptError):
            sw.canonical_value(THE_CONTROL, bad)


def test_the_target_is_respelled_in_the_admitted_words_or_refused_before_a_token():
    asked = "Share  profile updates / Share key profile updates :: OFF"
    want = "Share profile updates / Share key profile updates :: off"
    assert sw.canonical_target(asked, _JOIN) == want
    assert sw.canonical_target(want, _JOIN) == want  # idempotent
    assert sw.resolve_target(want, _JOIN) == (THE_PAGE, THE_CONTROL, "off")
    assert sw.page_url_for_target(want, _JOIN) == THE_PAGE.url
    for bad in (
        "Share profile updates / Share key profile updates",
        "Share profile updates :: on",
        "Share profile updates / Share key profile updates / x :: on",
        "Dark mode / Always on :: on",
        "Share profile updates / Share key profile updates :: sometimes",
    ):
        with pytest.raises(WriteAttemptError):
            sw.canonical_target(bad, _JOIN)


def _shot(**lists):
    base = {"switch": [], "checkbox": [], "radio": [], "select": [], "error": None, "too_many": False}
    base.update(lists)
    return base


@pytest.mark.parametrize(
    "label,control,before,after,reached,code",
    [
        ("switch moved alone", SYN_SWITCH, _shot(switch=[False, True]), _shot(switch=[True, True]), True, None),
        ("switch drawn as checkbox", SYN_SWITCH, _shot(checkbox=[False]), _shot(checkbox=[True]), True, None),
        ("another switch moved", SYN_SWITCH, _shot(switch=[False, True]), _shot(switch=[True, False]), True, "another_control_moved"),
        ("a radio moved beside a switch", SYN_SWITCH, _shot(switch=[False], radio=[True, False]), _shot(switch=[True], radio=[False, True]), True, "another_control_moved"),
        ("a select changed beside a switch", SYN_SWITCH, _shot(switch=[False], select=["a"]), _shot(switch=[True], select=["b"]), True, "another_control_moved"),
        ("switch never reached", SYN_SWITCH, _shot(switch=[False]), _shot(switch=[False]), False, "the_control_did_not_move"),
        ("radio group moved alone", SYN_RADIO, _shot(radio=[True, False, False]), _shot(radio=[False, True, False]), True, None),
        ("radio group and a switch", SYN_RADIO, _shot(radio=[True, False], switch=[False]), _shot(radio=[False, True], switch=[True]), True, "another_control_moved"),
        ("select moved alone", SYN_SELECT, _shot(select=["a", "n"]), _shot(select=["b", "n"]), True, None),
        ("two selects moved", SYN_SELECT, _shot(select=["a", "n"]), _shot(select=["b", "s"]), True, "another_control_moved"),
        ("page redrew", SYN_SWITCH, _shot(switch=[False]), _shot(switch=[True, False]), True, "page_redrew"),
        ("before unreadable", SYN_SWITCH, _shot(error="TimeoutError"), _shot(switch=[True]), True, "unreadable"),
        ("after too many", SYN_SWITCH, _shot(switch=[False]), _shot(too_many=True), True, "unreadable"),
        ("no snapshot", SYN_SWITCH, None, _shot(), True, "unreadable"),
    ],
)
def test_only_that_control_moved(label, control, before, after, reached, code):
    verdict = sw.only_that_control_moved(before, after, control, reached=reached)
    assert verdict["proceed"] is (code is None), (label, verdict)
    assert verdict["code"] == code, (label, verdict)


def test_THIS_CONTROL_CAN_FAIL_a_lax_expectation_lets_another_switch_through(monkeypatch):
    """The ``another_control_moved`` refusal is the expectation table, shown
    failing: loosened to 'at least one moved', a press that also flipped a
    second switch proceeds."""
    before, after = _shot(switch=[False, True]), _shot(switch=[True, False])
    assert sw.only_that_control_moved(before, after, SYN_SWITCH, reached=True)["code"] == "another_control_moved"
    lax = dict(sw._EXPECTED_MOVES)
    lax[sw.SWITCH] = {"switch+checkbox": 2, "radio": 0, "select": 0}
    monkeypatch.setattr(sw, "_EXPECTED_MOVES", lax)
    assert sw.only_that_control_moved(before, after, SYN_SWITCH, reached=True)["proceed"] is True


def test_the_direction_names_from_and_to_and_refuses_a_no_op():
    block = sw.direction_block(THE_CONTROL, "off", "on")
    assert (block["currently"], block["after"]) == ("off", "on")
    assert block["what_it_will_mean"] == sw.meaning_of(THE_CONTROL, "on") != ""
    for current, destination in (("off", "off"), ("maybe", "on"), ("off", "maybe")):
        with pytest.raises(WriteAttemptError):
            sw.direction_block(THE_CONTROL, current, destination)


def test_the_restore_call_is_exact_and_absent_when_nothing_was_read():
    call = sw.restore_call(THE_PAGE, THE_CONTROL, "off")
    assert call.startswith(
        "linkedin_set_admitted_setting(page='Share profile updates', "
        "control='Share key profile updates', value='off')"
    )
    assert sw.restore_call(THE_PAGE, THE_CONTROL, None) is None
    assert sw.restore_call(THE_PAGE, THE_CONTROL, "unknown") is None


def test_a_landing_elsewhere_reads_unknown_whatever_the_page_drew():
    good = {"reading": "off", "why": "w"}
    assert sw.state_of(good, THE_CONTROL, served=True) == ("off", "w")
    assert sw.state_of(good, THE_CONTROL, served=False)[0] == sw.UNKNOWN
    assert sw.state_of({"reading": "unknown", "why": "x"}, THE_CONTROL, served=True)[0] == sw.UNKNOWN
    assert sw.served_at(THE_PAGE, THE_PAGE.url + "/?trk=x")
    assert not sw.served_at(THE_PAGE, "https://www.linkedin.com/mypreferences/d/categories/account")
    assert not sw.served_at(THE_PAGE, "")


def test_the_preview_facts_name_the_page_the_control_and_the_live_proof_class():
    facts = sw.preview_facts(THE_PAGE, THE_CONTROL, {"named": 1, "role": "switch"})
    assert facts["page"] == "Share profile updates"
    assert facts["control"] == "Share key profile updates"
    assert facts["values"] == ["on", "off"]
    assert facts["stored_by"].startswith("the press itself")
    assert facts["live_proof"] == sw.LIVE_PROOF_ALLOWED
    assert facts["ruling"] == "HIS-OWN-SETTINGS-NOT-OUTWARD"


def test_a_selector_is_built_for_the_read_role_and_never_from_an_unsafe_name():
    assert sw.press_for(THE_CONTROL, "on", {"role": "switch"}) == (
        'role=switch[name="Share key profile updates"s]', "click")
    assert sw.press_for(SYN_RADIO, "Always", {"role": "radio"}) == ('role=radio[name="Always"s]', "click")
    assert sw.press_for(SYN_SELECT, "Gamma", {"role": "combobox"}) == (
        'role=combobox[name="Synthetic language"s]', "select_option")
    with pytest.raises(WriteAttemptError):
        sw.press_for(THE_CONTROL, "on", {"role": None})
    with pytest.raises(WriteAttemptError):
        sw.press_for(dataclasses.replace(SYN_RADIO, values=('A"]',)), 'A"]', {"role": "radio"})


# ---------------------------------------------------------------------------
# 3. The readers on the three synthetic patterns
# ---------------------------------------------------------------------------


async def _set(page, html: str) -> None:
    await page.set_content(html, wait_until="domcontentloaded")


async def test_the_switch_reader_and_a_press_on_div_switches(browser_page):
    page = browser_page
    await _set(page, world(SWITCH_MARKUP))
    first = await sw.read_control(page, SYN_SWITCH)
    assert (first["reading"], first["role"], first["named"], first["error"]) == ("off", "switch", 1, None)

    await _set(page, world(SWITCH_MARKUP, duplicateName=True))
    assert (await sw.read_control(page, SYN_SWITCH))["reading"] == sw.UNKNOWN

    for label, config, reached, code in (
        ("clean", {}, True, None),
        ("late", {"lateMs": 600}, True, None),
        ("inert", {"inert": True}, False, "the_control_did_not_move"),
        ("also flips the other", {"alsoFlip": True}, True, "another_control_moved"),
    ):
        await _set(page, world(SWITCH_MARKUP, **config))
        before = await sw.snapshot(page)
        assert sw.snapshot_counts(before)["switches"] == 2, label
        selector, kind = sw.press_for(SYN_SWITCH, "on", await sw.read_control(page, SYN_SWITCH))
        await page.click(selector)
        after_reading, wait = await profile_editor.wait_for_state(
            page,
            lambda: sw.read_control(page, SYN_SWITCH),
            lambda reading: sw.reads(reading, "on"),
            poll_ms=100,
        )
        after = await sw.snapshot(page)
        verdict = sw.only_that_control_moved(before, after, SYN_SWITCH, reached=wait["reached"])
        assert wait["reached"] is reached, (label, wait)
        assert verdict["code"] == code, (label, verdict)
        assert await page.evaluate("() => window.__presses") == 1, label


async def test_the_radio_group_reader_and_a_press_on_the_destination(browser_page):
    page = browser_page
    await _set(page, world(RADIO_MARKUP))
    reading = await sw.read_control(page, SYN_RADIO)
    assert (reading["reading"], reading["role"], reading["named"]) == ("Never", "radio", 1)

    for label, config in (("an undeclared choice", {"extraChoice": True}),
                          ("nothing checked", {"noneChecked": True})):
        await _set(page, world(RADIO_MARKUP, **config))
        assert (await sw.read_control(page, SYN_RADIO))["reading"] == sw.UNKNOWN, label

    for label, config, reached, code in (
        ("clean", {}, True, None),
        ("late", {"lateMs": 600}, True, None),
        ("inert", {"inert": True}, False, "the_control_did_not_move"),
        ("also flips the switch", {"alsoFlip": True}, True, "another_control_moved"),
    ):
        await _set(page, world(RADIO_MARKUP, **config))
        before = await sw.snapshot(page)
        selector, kind = sw.press_for(SYN_RADIO, "Always", await sw.read_control(page, SYN_RADIO))
        assert kind == "click"
        await page.click(selector)
        _after, wait = await profile_editor.wait_for_state(
            page,
            lambda: sw.read_control(page, SYN_RADIO),
            lambda r: sw.reads(r, "Always"),
            poll_ms=100,
        )
        verdict = sw.only_that_control_moved(
            before, await sw.snapshot(page), SYN_RADIO, reached=wait["reached"]
        )
        assert wait["reached"] is reached, (label, wait)
        assert verdict["code"] == code, (label, verdict)


async def test_the_select_reader_the_choice_and_the_save_gate(browser_page):
    page = browser_page
    await _set(page, world(SELECT_MARKUP))
    reading = await sw.read_control(page, SYN_SELECT)
    assert (reading["reading"], reading["role"], reading["named"]) == ("Beta", "combobox", 1)

    await _set(page, world(SELECT_MARKUP, extraOption=True))
    assert (await sw.read_control(page, SYN_SELECT))["reading"] == sw.UNKNOWN

    for label, config, reached, code, save in (
        ("clean", {}, True, None, True),
        ("late", {"lateMs": 600}, True, None, True),
        ("also changes the region", {"alsoChange": True}, True, "another_control_moved", True),
        ("two saves", {"twoSaves": True}, True, None, False),
        ("disabled save", {"disabledSave": True}, True, None, False),
        ("no save drawn", {"noSave": True}, True, None, False),
    ):
        await _set(page, world(SELECT_MARKUP, **config))
        before = await sw.snapshot(page)
        selector, kind = sw.press_for(SYN_SELECT, "Gamma", await sw.read_control(page, SYN_SELECT))
        assert kind == "select_option"
        await page.select_option(selector, label="Gamma")
        _after, wait = await profile_editor.wait_for_state(
            page,
            lambda: sw.read_control(page, SYN_SELECT),
            lambda r: sw.reads(r, "Gamma"),
            poll_ms=100,
        )
        verdict = sw.only_that_control_moved(
            before, await sw.snapshot(page), SYN_SELECT, reached=wait["reached"]
        )
        assert wait["reached"] is reached, (label, wait)
        assert verdict["code"] == code, (label, verdict)
        gate = await sw.save_gate(page, SYN_SELECT_PAGE)
        assert gate["needed"] is True
        assert gate["proceed"] is save, (label, gate)
        if save:
            assert gate["selector"] == 'role=button[name="Save"s]'


async def test_the_snapshot_never_returns_what_a_select_holds(browser_page):
    page = browser_page
    await _set(page, world(SELECT_MARKUP))
    shot = await sw.snapshot(page)
    counts = sw.snapshot_counts(shot)
    assert counts == {"switches": 0, "checkboxes": 0, "radios": 0, "selects": 2,
                      "error": None, "too_many": False}
    assert "v-b" not in json.dumps(counts) and "r-1" not in json.dumps(counts)


# ---------------------------------------------------------------------------
# 4. The real page: "Share profile updates", the live lane's capture
# ---------------------------------------------------------------------------


async def _refused(route) -> None:
    await route.abort()


async def _serve_the_capture(page) -> None:
    """The skeleton keeps stylesheet and image path words, so every request
    the page would make is refused first, as ``tests/network_guard.py`` asks."""
    await page.route("**/*", _refused)
    await page.set_content(REAL_CAPTURE.read_text(encoding="ascii"), wait_until="domcontentloaded")


async def test_the_real_page_draws_what_the_admitted_record_says(browser_page):
    """THE RECORD IS A MEASUREMENT OF THIS PAGE, held here: one switch named
    exactly as admitted, read off, no Save and no form in ``main`` -- which is
    what ``save_label=None`` rests on -- and nothing else checkable or
    choosable anywhere on the page."""
    page = browser_page
    await _serve_the_capture(page)
    reading = await sw.read_control(page, THE_CONTROL)
    assert (reading["reading"], reading["role"], reading["named"], reading["error"]) == (
        "off", "switch", 1, None)
    assert await page.locator("main button").count() == 0
    assert await page.locator("main form").count() == 0
    assert await page.get_by_role("heading", name=THE_PAGE.name, exact=True).count() == 1
    counts = sw.snapshot_counts(await sw.snapshot(page))
    assert counts == {"switches": 1, "checkboxes": 0, "radios": 0, "selects": 0,
                      "error": None, "too_many": False}
    gate = await sw.save_gate(page, THE_PAGE)
    assert (gate["needed"], gate["proceed"]) == (False, False)
    assert sw.press_for(THE_CONTROL, "on", reading) == (
        'role=switch[name="Share key profile updates"s]', "click")


async def test_the_real_switch_pressed_reads_on_and_nothing_else_moved(browser_page):
    """The real skeleton's input is a native checkbox, so a press flips its
    own ``checked`` property in the browser -- what the press does LIVE is
    the live proof's question; this holds the reader, the selector, the wait
    and the only-it-moved verdict on the page as captured."""
    page = browser_page
    await _serve_the_capture(page)
    before = await sw.snapshot(page)
    selector, _kind = sw.press_for(THE_CONTROL, "on", await sw.read_control(page, THE_CONTROL))
    await page.click(selector)
    after_reading, wait = await profile_editor.wait_for_state(
        page,
        lambda: sw.read_control(page, THE_CONTROL),
        lambda r: sw.reads(r, "on"),
        poll_ms=100,
    )
    assert wait["reached"] is True, after_reading
    verdict = sw.only_that_control_moved(before, await sw.snapshot(page), THE_CONTROL, reached=True)
    assert verdict["proceed"] is True, verdict


async def test_the_index_name_and_the_heading_name_no_control_on_the_real_page(browser_page):
    """Why the control is admitted by ITS label: the settings index calls the
    setting "Sharing profile edits" and the page's heading is "Share profile
    updates"; neither names the switch, so neither may be used to aim it."""
    page = browser_page
    await _serve_the_capture(page)
    for wrong in ("Sharing profile edits", THE_PAGE.name):
        control = dataclasses.replace(THE_CONTROL, label=wrong)
        assert (await sw.read_control(page, control))["reading"] == sw.UNKNOWN, wrong
