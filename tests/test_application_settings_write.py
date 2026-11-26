"""His application settings page, admitted BY NAME for writing: its two switches.

Lane build-jobs2, 2026-11-26, applying APPLICATION-SETTINGS-WRITE (the
orchestrator, 2026-11-26): "admitted in principle (his own switches, a
reversible on/off pair behind the grant, proven by a live round trip)". Census
rows ``J 74`` / ``P M8`` (share resume data with hirers) and ``J 76`` /
``P M7`` (save resumes and application data).

THE PAGE IS THE LIVE LANE'S SESSION-11 CAPTURE (load 11), with LinkedIn's words
measured by keyed shape: ``tests/fixtures/live11/application_settings_words.html``.
Its main region draws one ``h1`` reading ``Resumes and application data`` and
two ``input[role=switch][type=checkbox]``, each named by its own ``<label
for>``, both ``aria-checked="true"``, and no Save. A skeleton keeps attributes,
not DOM properties, so the ``checked`` PROPERTY each switch held is not in the
file: the world AS DRAWN below adds ``checked`` to both inputs -- DERIVED, and
said so, from the measured ``aria-checked="true"``. The press-time world adds
one script standing in for LinkedIn's toggle, which keeps ``aria-checked``
equal to the property; without it a native click flips the property alone and
the writer reads the disagreement as ``unknown``, which is what it should do.

NOTHING HERE REACHES LINKEDIN: every load is ``set_content`` of a frozen world,
and every request a page would make is refused first.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from linkedin_server import application_settings, readonly, settings_writer as sw, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

_ACTION = "set_admitted_setting"
_FIXTURES = Path(__file__).parent / "fixtures" / "live11"
_WORDS = (_FIXTURES / "application_settings_words.html").read_text(encoding="ascii")
_REDUCED = (_FIXTURES / "application_settings.html").read_text(encoding="ascii")

_PAGE = "Resumes and application data"
_SAVE = "Allow LinkedIn to save your resumes and answers"
_SHARE = "Allow recruiters to view your resumes"
_URL = application_settings.PAGE_URL

#: Each switch's input, exactly as the capture draws it (its id is the keyed
#: reference the label's ``for`` names).
_SAVE_INPUT = ('<input role="switch" aria-checked="true" class="input artdeco-toggle__button " '
               'data-artdeco-toggle-button="x" id="kb5e0cfaa" type="checkbox">')
_SHARE_INPUT = ('<input role="switch" aria-checked="true" class="input artdeco-toggle__button " '
                'data-artdeco-toggle-button="x" id="kf67a4379" type="checkbox">')


def _swap(markup: str, old: str, new: str) -> str:
    assert markup.count(old) == 1, old
    return markup.replace(old, new)


def _drawn(markup: str = _WORDS) -> str:
    """The capture AS DRAWN: both switches on, the property set beside the
    measured ``aria-checked``."""
    for tag in (_SAVE_INPUT, _SHARE_INPUT):
        markup = _swap(markup, tag, tag[:-1] + " checked>")
    return markup


def _off(markup: str, tag: str) -> str:
    """One switch read off: its ``aria-checked`` and its property both."""
    drawn = tag[:-1] + " checked>"
    return _swap(markup, drawn, tag.replace('aria-checked="true"', 'aria-checked="false"'))


#: LinkedIn's toggle, modelled for the press: ``aria-checked`` follows the
#: property on every change, and a counter is kept for the witness. With
#: ``both`` set, one press flips the OTHER switch too -- the shape the check
#: after the press must refuse.
def _pressable(markup: str, *, both: bool = False) -> str:
    script = (
        "<script>window.__presses = 0; window.__saves = 0;"
        "document.addEventListener('change', function (e) {"
        " var t = e.target; if (!t.matches('input[role=switch]')) return;"
        " window.__presses += 1; t.setAttribute('aria-checked', String(t.checked));"
        + (" document.querySelectorAll('input[role=switch]').forEach(function (o) {"
           " if (o !== t) { o.checked = !o.checked; o.setAttribute('aria-checked', String(o.checked)); } });"
           if both else "")
        + "}, true);</script>"
    )
    return _swap(markup, "</head>", script + "</head>") if "</head>" in markup else script + markup


async def _refused(route) -> None:
    await route.abort()


class _Navigator:
    """Serves frozen worlds for the ONE admitted address, in order; the last
    repeats. ``witness`` holds the page's own counters read BEFORE each load
    replaces the page."""

    def __init__(self, *worlds: str):
        self.worlds = list(worlds)
        self.gotos: list[str] = []
        self.witness: list[dict] = []

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url != _URL:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        self.witness.append(await page.evaluate(
            "() => ({presses: window.__presses || 0, saves: window.__saves || 0})"))
        html = self.worlds.pop(0) if len(self.worlds) > 1 else self.worlds[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return url


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


def _record():
    return next(page for page in sw.ADMITTED_PAGES if page.name == _PAGE)


# ---------------------------------------------------------------------------
# 1. The admission: by name, from the capture, at the read door's own address
# ---------------------------------------------------------------------------


def test_the_page_is_admitted_by_its_heading_with_its_two_switches():
    record = _record()
    assert record.address == _URL
    assert readonly.is_read_url(_URL)
    assert record.save_label is None  # measured: no Save; each switch stores itself
    assert [c.label for c in record.controls] == [_SAVE, _SHARE]
    # The labels are the reader's own, so the read and the write name one
    # switch by one string.
    assert set(application_settings.SWITCHES) == {_SAVE, _SHARE}
    save, share = record.controls
    assert (save.kind, share.kind) == (sw.SWITCH, sw.SWITCH)
    assert save.rows == ("J 76", "P M7") and share.rows == ("J 74", "P M8")
    # Recruiters see the second switch's effect; nobody sees the first's.
    assert share.visible_to_others is True and save.visible_to_others is False
    for control in record.controls:
        assert control.live_proof in sw.LIVE_PROOF_CLASSES
        assert {v for v, _ in control.meanings} == set(sw.SWITCH_VALUES)
    assert "tests/fixtures/live11/application_settings_words.html" in record.capture
    assert "APPLICATION-SETTINGS-WRITE" in record.admitted_by
    assert sw.resolve(_PAGE, _SHARE) == (record, share)
    assert sw.resolve(" Resumes  and application data ", _SAVE) == (record, save)
    for page_name, label in ((_PAGE.lower(), _SAVE), (_PAGE, _SAVE.lower()), (_PAGE, "Upload resume")):
        with pytest.raises(WriteAttemptError):
            sw.resolve(page_name, label)


def test_the_write_pattern_admits_the_two_addresses_and_nothing_beside_them():
    pattern = writes.spec_for_action(_ACTION).url_pattern
    assert pattern.match(_URL) and pattern.match(_URL.rstrip("/"))
    assert pattern.match(sw.SHARE_PROFILE_UPDATES.address)
    for other in (
        "https://www.linkedin.com/jobs/application-settings/x",
        "https://www.linkedin.com/jobs/application-settings/?x=1",
        "https://www.linkedin.com/jobs/application/",
        "https://www.linkedin.com/jobs/applications-settings/",
        "http://www.linkedin.com/jobs/application-settings/",
    ):
        assert not pattern.match(other), other


# ---------------------------------------------------------------------------
# 2. The write door: ONE substring excused, for this ONE address
# ---------------------------------------------------------------------------


def _grant(value: str = "off", label: str = _SHARE) -> writes.WriteGrant:
    return writes.WriteGrant(
        action=_ACTION, target=f"{_PAGE} / {label} :: {value}", token="t", minted_at=0.0
    )


def test_the_write_door_admits_the_page_excusing_jobs_application_at_this_address_alone():
    assert writes.assert_write_url(_URL, _grant()) == _URL
    spec = writes.spec_for_action(_ACTION)
    # The address trips two forbidden entries, measured with the shipped tuple.
    assert [b for b in readonly._FORBIDDEN_URL_SUBSTRINGS if b in _URL] == ["/jobs/application", "settings"]
    # "settings" is the spec's own, for every admitted page; "/jobs/application"
    # is excused for this ONE address, by equality, and is no spec-wide word.
    assert "/jobs/application" not in spec.exempt_substrings
    assert spec.exempt_substring is None
    assert dict(spec.exempt_substrings_at) == {_URL: frozenset({"/jobs/application"})}
    # No other spec excuses it anywhere.
    for other in writes.SANCTIONED_WRITES.values():
        if other.action != _ACTION:
            assert not other.exempt_substrings_at, other.action
            assert other.exempt_substring != "/jobs/application", other.action


def test_THIS_CONTROL_CAN_FAIL_the_excusal_does_not_follow_a_second_address(monkeypatch):
    """The excusal is keyed by the ADDRESS, not by the action: a second page
    registered under ``/jobs/application/`` and admitted by a widened pattern
    is still refused on that word. A spec-wide excusal would let it through --
    the shape this table was built not to have."""
    elsewhere = "https://www.linkedin.com/jobs/application/synthetic-settings/"
    record = dataclasses.replace(_record(), name="Synthetic jobs page", address=elsewhere)
    monkeypatch.setattr(sw, "ADMITTED_PAGES", sw.ADMITTED_PAGES + (record,))
    spec = writes.spec_for_action(_ACTION)
    widened = dataclasses.replace(spec, url_pattern=sw.admitted_address_pattern())
    monkeypatch.setitem(writes.SANCTIONED_WRITES, spec.tool_name, widened)
    grant = writes.WriteGrant(
        action=_ACTION, target=f"Synthetic jobs page / {_SHARE} :: off", token="t", minted_at=0.0
    )
    with pytest.raises(WriteAttemptError) as caught:
        writes.assert_write_url(elsewhere, grant)
    assert "'/jobs/application'" in str(caught.value)
    # The control's other half: the same widened spec, excused spec-wide, admits it.
    spread = dataclasses.replace(widened, exempt_substrings=widened.exempt_substrings + ("/jobs/application",))
    monkeypatch.setitem(writes.SANCTIONED_WRITES, spec.tool_name, spread)
    assert writes.assert_write_url(elsewhere, grant) == elsewhere


# ---------------------------------------------------------------------------
# 3. The audiences, re-keyed by the whole target
# ---------------------------------------------------------------------------


def test_the_audiences_are_keyed_by_page_control_and_value_so_two_switches_cannot_collide():
    keys = set(sw.audiences())
    want = {
        f"{page.name} / {control.label} :: {value}".casefold()
        for page in sw.ADMITTED_PAGES
        for control in page.controls
        for value in control.values
    }
    assert keys == want and len(keys) == 6
    assert set(writes.spec_for_action(_ACTION).audiences) == want
    # Each key's sentence names its own control, so a reader of any one of
    # them cannot be handed another control's meaning.
    for key, sentence in sw.audiences().items():
        page_and_control = key.split(" :: ")[0]
        assert sentence.casefold().startswith(page_and_control + ": "), key
    # The join is the target's own.
    assert sw.TARGET_JOIN_SPELLING == writes.TARGET_JOIN


def test_THIS_CONTROL_CAN_FAIL_the_same_control_admitted_twice_is_refused(monkeypatch):
    monkeypatch.setattr(sw, "ADMITTED_PAGES", sw.ADMITTED_PAGES + (_record(),))
    with pytest.raises(ValueError):
        sw.audiences()


def test_a_click_time_reading_is_judged_against_its_own_control():
    spec = writes.spec_for_action(_ACTION)
    target = f"{_PAGE} / {_SHARE} :: off"
    assert writes.valid_from(spec, "on", target) == (True, "")
    for state in ("off", "unknown", "On"):
        ok, why = writes.valid_from(spec, state, target)
        assert ok is False and why, state


# ---------------------------------------------------------------------------
# 4. The page through the shipped doors
# ---------------------------------------------------------------------------


async def test_each_switch_is_read_by_its_own_label_and_the_words_are_the_anchor(browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    save, share = _record().controls
    await page.set_content(_drawn(), wait_until="domcontentloaded")
    for control in (save, share):
        reading = await sw.read_control(page, control)
        assert (reading["reading"], reading["named"], reading["role"]) == ("on", 1, "switch"), control.label
    await page.set_content(_off(_drawn(), _SHARE_INPUT), wait_until="domcontentloaded")
    assert (await sw.read_control(page, share))["reading"] == "off"
    assert (await sw.read_control(page, save))["reading"] == "on"
    # As captured, with no property: aria says on and the property says off,
    # and a disagreement is never a value.
    await page.set_content(_WORDS, wait_until="domcontentloaded")
    assert (await sw.read_control(page, share))["reading"] == "unknown"
    # The tracked copy with its words reduced names no switch at all.
    await page.set_content(_drawn(_REDUCED), wait_until="domcontentloaded")
    reading = await sw.read_control(page, share)
    assert (reading["reading"], reading["named"]) == ("unknown", 0)


async def _granted(page, label: str, value: str, *worlds: str):
    nav = _Navigator(*worlds)
    target = {"setting": f"{_PAGE} / {label}", "value": value}
    block = await preview(spec_for_action(_ACTION), target=target, navigator=nav, page=page, to_state=value)
    grant = consume(block["to_confirm"], action=_ACTION, target=target)
    return grant, block, nav


async def test_the_share_switch_off_and_back_on_each_verified_on_a_fresh_render(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    drawn, shared_off = _drawn(), _off(_drawn(), _SHARE_INPUT)
    grant, block, nav = await _granted(page, _SHARE, "off", drawn)
    assert nav.gotos == [_URL]
    text = json.dumps(block)
    assert _PAGE in text and _SHARE in text
    assert block["direction"]["currently"] == "on" and block["direction"]["after"] == "off"
    assert block["who_can_see_it"] == "other members can see it"
    act = _Navigator(_pressable(drawn), shared_off)
    receipt = await writes.perform(act, page, grant)
    assert receipt["performed"] is True, receipt
    assert act.gotos == [_URL, _URL]
    assert act.witness[1]["presses"] == 1, act.witness
    press = receipt["setting_press"]
    assert press["check"]["proceed"] is True and press["save"]["needed"] is False, press
    assert "stop" not in press, press
    assert receipt["restore"]["previous_value"] == "on"
    assert "value='on'" in receipt["restore"]["to_put_it_back"]
    writes.discard_all()
    # AND BACK, the round trip the ruling names, through the same doors.
    grant, block, _nav = await _granted(page, _SHARE, "on", shared_off)
    assert block["direction"]["currently"] == "off"
    act = _Navigator(_pressable(shared_off), drawn)
    receipt = await writes.perform(act, page, grant)
    assert receipt["performed"] is True, receipt
    assert receipt["restore"]["previous_value"] == "off"


async def test_a_press_that_also_moves_the_other_switch_is_a_STOP(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    drawn = _drawn()
    grant, _block, _nav = await _granted(page, _SAVE, "off", drawn)
    act = _Navigator(_pressable(drawn, both=True), _off(_off(drawn, _SAVE_INPUT), _SHARE_INPUT))
    receipt = await writes.perform(act, page, grant)
    press = receipt["setting_press"]
    assert press["check"]["code"] == "another_control_moved", press
    assert press["stop"].startswith("STOP. This page stores on the press"), press


async def test_a_no_op_and_an_unadmitted_control_load_nothing_and_mint_nothing(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    with pytest.raises(WriteAttemptError):
        await preview(spec_for_action(_ACTION), target={"setting": f"{_PAGE} / {_SHARE}", "value": "on"},
                      navigator=_Navigator(_drawn()), page=page, to_state="on")
    for setting in (f"{_PAGE} / Upload resume", f"{_PAGE} / Show options", "Resumes / " + _SAVE):
        nav = _Navigator(_drawn())
        with pytest.raises(WriteAttemptError):
            await preview(spec_for_action(_ACTION), target={"setting": setting, "value": "off"},
                          navigator=nav, page=page, to_state="off")
        assert nav.gotos == [], setting
    assert writes._GRANTS == {}
