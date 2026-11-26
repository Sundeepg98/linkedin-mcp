"""The live lane's session-2 harness, offline: each guard it carries, shown working and shown failing.

``scripts/_probe_live_lane_session_2.py`` is written under
PAGE-MAY-VETO-NEVER-SUPPLY: every address is a constant or one of the
package's composers filled from the caller's ``--item``, and a page may only
VETO. This file holds that and everything else the harness promises, with no
Chrome of his, no network and no LinkedIn:

* selection -- nothing by default, closed items, riders after their page;
* addresses -- admitted, and moved by the caller's item and by nothing else;
  the navigation guard's own engine finds no derived site in the file and
  DOES find one planted into a copy;
* the three vetoes, both ways;
* the ledger -- the 41st load and the 6th search refused BEFORE navigating,
  a refused address uncounted, one driver at a time;
* what is written -- a skeleton keeps what a reader's selectors need and
  nothing that names anybody; a reduced envelope keeps the evidence and
  shapes the rest;
* the press flow -- a click, a reading by attribute, Escape, and the two
  anomalies (a menu that stays open, a conversation opened) -- end to end in
  a local headless Chromium over ``set_content``;
* the setting's offline check -- the (b) reader over its own capture, its
  seven verdicts, and the case a capture CANNOT answer (a state held in the
  checked property alone), reproduced rather than argued;
* lane D's LQ-4 filter -- only the download-behaviour lines are kept, and a
  decoy line naming a tab never survives.
* lane D's LQ-4 count, hermetic -- the attach child counts in a temp directory
  of its own, so a folder another process leaves in the system temp is never
  counted, a folder the child leaves still fails, and the directory is emptied
  only under the session's own state.

Every literal here is invented: the names are the redaction tests' own
invented ones, the slug is ``tests/test_no_committed_identity.py``'s
sanctioned synthetic slug, and every long digit run is built at runtime.
"""
from __future__ import annotations

import ast
import asyncio
import contextlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _probe_live_lane_session_2 as harness  # noqa: E402
from linkedin_server import profile_editor, readonly  # noqa: E402
from tests.test_writes import browser_page  # noqa: E402,F401 -- fixture

SOURCE_PATH = ROOT / "scripts" / "_probe_live_lane_session_2.py"
KEY = bytes(range(32))
OTHER_KEY = bytes(range(1, 33))

#: Invented, and the redaction tests' own: no real person.
INVENTED_NAME = "Dara Whitfield"
#: tests/test_no_committed_identity.py's sanctioned synthetic slug.
SYNTHETIC_SLUG = "some-real-slug-99"


def _digits(n: int, seed: str = "7") -> str:
    # BUILT AT RUNTIME: a long digit run written out in a tracked file is the
    # shape tests/test_no_committed_identity.py refuses.
    return seed * n


ITEMS = {
    "activity": _digits(19, "3"),
    "posting": _digits(10, "4"),
    "org": _digits(7, "5"),
    "past_org": _digits(6, "6"),
    "group": _digits(8, "7"),
    "school": _digits(5, "8"),
    "event": _digits(19, "9"),
    "thread": "2-abc",
}


# --------------------------------------------------------------------------
# Selection and items -- decided before the browser is touched.
# --------------------------------------------------------------------------


def test_nothing_fires_by_default() -> None:
    with pytest.raises(SystemExit):
        harness.selected([], {})


def test_an_unknown_key_or_a_repeat_is_refused() -> None:
    with pytest.raises(SystemExit):
        harness.selected(["--only", "setting,inbox"], {})
    with pytest.raises(SystemExit):
        harness.selected(["--only", "setting,setting"], {})


@pytest.mark.parametrize("key", sorted(k for k, v in harness.KEYS.items() if v.get("items")))
def test_a_key_that_needs_an_item_refuses_without_it(key: str) -> None:
    with pytest.raises(SystemExit):
        harness.selected(["--only", key], {})
    wanted = dict((name, ITEMS[name]) for name in harness.KEYS[key]["items"])
    assert harness.selected(["--only", key], wanted) == [key]


@pytest.mark.parametrize("argv", [
    ["--item", "org=12ab"],
    ["--item", "org=" + _digits(21)],
    ["--item", "org=" + chr(0x0661) + chr(0x0662)],
    ["--item", "org="],
    ["--item", "person=123"],
    ["--item", "org=1", "--item", "org=2"],
    ["--item", "org"],
    ["--item"],
    ["--item", "thread=abc"],
])
def test_an_item_outside_its_closed_shape_is_refused(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as refused:
        harness.parse_items(argv)
    assert "12ab" not in str(refused.value) and _digits(21) not in str(refused.value)


def test_items_of_their_shape_are_taken() -> None:
    argv = []
    for name, value in ITEMS.items():
        argv += ["--item", name + "=" + value]
    assert harness.parse_items(argv) == ITEMS


def test_riders_need_their_page_earlier_in_the_run() -> None:
    with pytest.raises(SystemExit):
        harness.selected(["--only", "in_me_more"], {})
    with pytest.raises(SystemExit):
        harness.selected(["--only", "in_me_more,in_me"], {})
    assert harness.selected(["--only", "in_me,in_me_more,me_menu"], {}) == [
        "in_me", "in_me_more", "me_menu"]
    assert harness.selected(["--only", "activity_all,me_menu"], {}) == ["activity_all", "me_menu"]


@pytest.mark.parametrize("alone", ["setting_offline", "attach_check"])
def test_the_offline_and_attach_keys_run_alone(alone: str) -> None:
    assert harness.selected(["--only", alone], {}) == [alone]
    with pytest.raises(SystemExit):
        harness.selected(["--only", alone + ",setting"], {})


# --------------------------------------------------------------------------
# Addresses: admitted, and moved by the caller's item and nothing else.
# --------------------------------------------------------------------------

CAPTURE_KEYS = sorted(k for k, v in harness.KEYS.items() if v["kind"] == "capture")


@pytest.mark.parametrize("key", CAPTURE_KEYS)
def test_every_capture_address_is_admitted(key: str) -> None:
    url = harness.address_for(key, ITEMS)
    assert url is not None and readonly.is_read_url(url), key


@pytest.mark.parametrize("key", [k for k in CAPTURE_KEYS if harness.KEYS[k].get("items")])
def test_the_callers_item_is_the_only_moving_part(key: str) -> None:
    """THE RULE, as a property: change the item and the address moves with
    it, carrying the new value; hold it and the address holds."""
    name = harness.KEYS[key]["items"][0]
    moved = dict(ITEMS)
    moved[name] = "1" + ITEMS[name][1:] if ITEMS[name][0] != "1" else "2" + ITEMS[name][1:]
    first = harness.address_for(key, ITEMS)
    again = harness.address_for(key, dict(ITEMS))
    second = harness.address_for(key, moved)
    assert first == again
    assert first != second and moved[name] in second and ITEMS[name] in first


def test_a_composer_refusal_is_no_address() -> None:
    assert harness.address_for("company_people", {"org": "not-digits"}) is None
    assert harness.address_for("school_people", {"school": ""}) is None


@pytest.mark.parametrize("key", ["n104", "n161", "n179"])
def test_every_search_key_is_priced_as_a_search(key: str) -> None:
    from _probe_live_lane_session_1 import _surface_of

    assert harness.KEYS[key].get("searches") == 1
    assert _surface_of(harness.address_for(key, ITEMS)) == harness.SEARCH_SURFACE


def test_the_people_search_keys_are_priced_as_searches() -> None:
    assert {k for k, v in harness.KEYS.items() if v.get("searches")} == {
        "n94", "n84", "n87", "n104", "n161", "n179"}


def _nav():
    from tests import test_navigation_is_never_derived as nav

    return nav


def test_the_navigation_guard_finds_nothing_here() -> None:
    assert _nav().violations(SOURCE_PATH.read_text(encoding="utf-8"), SOURCE_PATH.name) == []


@pytest.mark.parametrize("original,planted,why", [
    (
        "    url = address_for(key, items)\n",
        '    url = address_for(key, {**items, "group": str(_json_or_none(STATE / "m.json"))})\n',
        "an item taken from a reading on disk instead of the caller",
    ),
    (
        "        landed = await BROWSER.goto(page, url)\n        relation = l1._relation(landed, url)\n",
        "        landed = await BROWSER.goto(page, url)\n        await BROWSER.goto(page, landed)\n"
        "        relation = l1._relation(landed, url)\n",
        "a navigation to where the last one landed",
    ),
])
def test_the_navigation_guard_goes_red_on_a_derivation_planted_here(original, planted, why) -> None:
    """SHOWN FAILING: the same engine, on a copy of THIS file with one line
    changed, finds the derived site -- so its silence above is a reading."""
    source = SOURCE_PATH.read_text(encoding="utf-8")
    assert source.count(original) == 1, why
    assert _nav().violations(source.replace(original, planted), SOURCE_PATH.name), why


def test_neither_harness_is_declared_as_deriving_a_navigation() -> None:
    declared = _nav().KNOWN_DERIVED_NAVIGATIONS
    assert "_probe_live_lane_session_2.py" not in declared
    assert "_probe_live_lane_session_1.py" not in declared


# --------------------------------------------------------------------------
# The vetoes: a reading may say no; it never supplies.
# --------------------------------------------------------------------------


def _memberships(ids, suggestions=()):
    return {"memberships": {"identifiers": list(ids)}, "others": {"identifiers": list(suggestions)}}


def test_a_group_he_belongs_to_passes_and_a_suggestion_does_not() -> None:
    group = ITEMS["group"]
    assert harness.veto_group(group, _memberships([group])) is None
    assert harness.veto_group(group, _memberships([], suggestions=[group])) is not None
    assert harness.veto_group(group, None) is not None
    assert harness.veto_group(group, {"memberships": {}}) is not None


def _activity(established, ids):
    return {"envelope": {"authorship": {"established": established},
                         "items": ["urn:li:activity:" + i for i in ids]}}


def test_his_post_passes_and_nothing_else_does() -> None:
    post = ITEMS["activity"]
    assert harness.veto_activity(post, _activity(True, [post])) is None
    assert harness.veto_activity(post, _activity(False, [post])) is not None
    assert harness.veto_activity(post, _activity(True, [_digits(19, "1")])) is not None
    assert harness.veto_activity(post, None) is not None


def test_attendees_run_only_after_their_own_event_drew_the_link() -> None:
    event = ITEMS["event"]
    shape = harness.value_shape(event, KEY)
    good = {"event_shape": shape, "attendees_link_drawn": True}
    assert harness.veto_attendees(event, good, KEY) is None
    assert harness.veto_attendees(event, dict(good, attendees_link_drawn=False), KEY) is not None
    assert harness.veto_attendees(_digits(19, "1"), good, KEY) is not None
    assert harness.veto_attendees(event, None, KEY) is not None


def test_the_group_veto_reads_the_envelope_the_harness_wrote(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(harness, "STATE", tmp_path)
    group = ITEMS["group"]
    (tmp_path / "memberships.json").write_text(
        json.dumps({"envelope": _memberships([group])}), encoding="utf-8")
    assert harness._veto_for("group_members", {"group": group}) is None
    assert harness._veto_for("group_home", {"group": _digits(8, "1")}) is not None


# --------------------------------------------------------------------------
# The ledger: loads, spacing, searches, one driver.
# --------------------------------------------------------------------------


def _loads(n: int, surface: str = "feed", at: float = 0.0) -> list[dict]:
    return [{"n": i + 1, "surface": surface, "at": at} for i in range(n)]


def test_the_budget_and_the_search_cap_as_pure_functions() -> None:
    assert harness.budget_verdict(_loads(38), 2) is None
    assert harness.budget_verdict(_loads(39), 2) is not None
    assert harness.search_verdict(_loads(4, "search"), 1) is None
    assert harness.search_verdict(_loads(4, "search") + _loads(3), 2) is not None
    assert harness.searches_spent(_loads(2, "search") + _loads(3)) == 2


class _FakeBrowser:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def goto(self, page, url, **kwargs):  # noqa: ANN001 - fake
        readonly.assert_read_url(url)
        self.calls.append(url)
        return url


@pytest.fixture()
def fake(tmp_path, monkeypatch):
    browser = _FakeBrowser()
    monkeypatch.setattr(harness, "BROWSER", browser)
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(harness, "MIN_GAP_S", 0.0)
    harness._install_counter()
    return browser


FEED = "https://www.linkedin.com/feed/"


def test_every_admitted_navigation_is_counted_with_its_surface(fake) -> None:
    asyncio.run(harness.BROWSER.goto(None, FEED))
    search = harness.address_for("n104", ITEMS)
    asyncio.run(harness.BROWSER.goto(None, search))
    ledger = json.loads(harness.LEDGER.read_text(encoding="utf-8"))
    assert [row["surface"] for row in ledger["loads"]] == ["feed", "search"]
    assert fake.calls == [FEED, search]


def test_the_ceiling_refuses_before_the_navigation(fake) -> None:
    harness.LEDGER.write_text(json.dumps({"loads": _loads(harness.CEILING)}), encoding="utf-8")
    with pytest.raises(harness._LedgerRefusal):
        asyncio.run(harness.BROWSER.goto(None, FEED))
    assert fake.calls == []


def test_the_sixth_search_is_refused_before_the_navigation(fake) -> None:
    harness.LEDGER.write_text(json.dumps({"loads": _loads(5, "search")}), encoding="utf-8")
    with pytest.raises(harness._LedgerRefusal):
        asyncio.run(harness.BROWSER.goto(None, harness.address_for("n161", ITEMS)))
    assert fake.calls == []
    asyncio.run(harness.BROWSER.goto(None, FEED))
    assert fake.calls == [FEED], "a load that is not a search is not held by the search cap"


def test_a_named_profile_load_through_the_second_door_is_counted(tmp_path, monkeypatch) -> None:
    """FOUND LIVE, 2026-09-28: the named-person door (``named_profile=True``)
    loads an address the read door refuses, and the first wrapper waved it
    through uncounted. It is a load, and the ledger counts it."""
    calls: list[tuple[str, bool]] = []

    class _SecondDoor:
        async def goto(self, page, url, **kwargs):  # noqa: ANN001 - fake
            calls.append((url, kwargs.get("named_profile") is True))
            return url

    monkeypatch.setattr(harness, "BROWSER", _SecondDoor())
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(harness, "MIN_GAP_S", 0.0)
    harness._install_counter()
    profile = "https://www.linkedin.com/in/" + SYNTHETIC_SLUG + "/"
    assert not readonly.is_read_url(profile)
    asyncio.run(harness.BROWSER.goto(None, profile, named_profile=True))
    ledger = json.loads(harness.LEDGER.read_text(encoding="utf-8"))
    assert [row["surface"] for row in ledger["loads"]] == ["in"]
    assert calls == [(profile, True)]


def test_a_detail_page_load_through_the_third_door_is_counted_and_spaced(tmp_path, monkeypatch) -> None:
    """FOUND LIVE, 2026-10-10 (session 9): lane NP's detail-page door
    (``named_profile_details_of=``) loads an address the read door refuses,
    and the wrapper waved it through uncounted and unspaced -- the load was
    counted by hand. It is a load: the ledger counts it and spaces it."""
    calls: list[tuple[str, object]] = []

    class _ThirdDoor:
        async def goto(self, page, url, **kwargs):  # noqa: ANN001 - fake
            calls.append((url, kwargs.get("named_profile_details_of")))
            return url

    monkeypatch.setattr(harness, "BROWSER", _ThirdDoor())
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(harness, "MIN_GAP_S", 0.4)
    harness.LEDGER.write_text(json.dumps({"loads": _loads(1, at=time.time())}), encoding="utf-8")
    harness._install_counter()
    details = "https://www.linkedin.com/in/" + SYNTHETIC_SLUG + "/details/interests/"
    assert not readonly.is_read_url(details)
    started = time.monotonic()
    asyncio.run(harness.BROWSER.goto(None, details, named_profile_details_of=SYNTHETIC_SLUG))
    assert time.monotonic() - started >= 0.3, "the third door was not spaced"
    ledger = json.loads(harness.LEDGER.read_text(encoding="utf-8"))
    assert [row["surface"] for row in ledger["loads"]] == ["feed", "in"]
    assert calls == [(details, SYNTHETIC_SLUG)]


def test_a_refused_address_is_not_a_load(fake) -> None:
    with pytest.raises(readonly.WriteAttemptError):
        asyncio.run(harness.BROWSER.goto(None, "https://www.linkedin.com/my-items/"))
    assert not harness.LEDGER.exists()


def test_the_gap_is_waited_out_across_processes(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(harness, "BROWSER", _FakeBrowser())
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(harness, "MIN_GAP_S", 0.4)
    harness.LEDGER.write_text(json.dumps({"loads": _loads(1, at=time.time())}), encoding="utf-8")
    harness._install_counter()
    started = time.monotonic()
    asyncio.run(harness.BROWSER.goto(None, FEED))
    assert time.monotonic() - started >= 0.3


def test_one_driver_at_a_time(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "DRIVER_LOCK", tmp_path / "driver.lock")
    assert harness._take_driver_lock() is None
    assert harness._take_driver_lock() is not None
    harness._release_driver_lock()
    assert harness._take_driver_lock() is None


def test_the_environment_refuses_without_attach_mode(monkeypatch) -> None:
    monkeypatch.setattr(harness.config, "CDP_ATTACH", False)
    assert harness._environment_refusal() is not None
    monkeypatch.setattr(harness.config, "CDP_ATTACH", True)
    monkeypatch.setattr(harness.config, "MIN_NAVIGATION_INTERVAL_S", 3.0)
    assert harness._environment_refusal() is not None
    monkeypatch.setattr(harness.config, "MIN_NAVIGATION_INTERVAL_S", 20.0)
    assert harness._environment_refusal() is None


# --------------------------------------------------------------------------
# What is written: shapes, skeletons, reduced envelopes.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("text", [INVENTED_NAME, SYNTHETIC_SLUG, _digits(19), "x"],
                         ids=["a_name", "a_slug", "a_digit_run", "one_letter"])
def test_a_shape_carries_no_part_of_its_input(text: str) -> None:
    shape = harness.value_shape(text, KEY)
    assert shape == harness.value_shape(text, KEY)
    assert shape != harness.value_shape(text, OTHER_KEY), "the hash is not keyed"
    assert "<" not in shape and ">" not in shape
    for part in (text[i:i + 3] for i in range(max(1, len(text) - 2))):
        if len(part) == 3 and not part.isdigit():
            assert part not in shape.split(":")[1], (text, shape)


PEOPLE_PAGE = (
    "<!doctype html><html><head><script>var secret = '" + INVENTED_NAME + "';</script>"
    "<style>.x{}</style></head><body><header><button type='button' aria-expanded='false'>"
    "<img alt='" + INVENTED_NAME + "'>Me</button></header><main>"
    "<!-- " + INVENTED_NAME + " -->"
    "<ul><li class='msg-conversation-listitem' data-test-hook='UNREAD'>"
    "<a href='https://www.linkedin.com/in/" + SYNTHETIC_SLUG + "/?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3A"
    + _digits(12) + "' aria-label='Select conversation with " + INVENTED_NAME + "'>"
    "<span class='msg-conversation-card__participant-names'>" + INVENTED_NAME + "</span></a>"
    "<a href='/feed/update/urn:li:activity:" + _digits(19) + "/'>More</a>"
    "<button aria-label='Star conversation' aria-pressed='false'></button>"
    "</li></ul>"
    "<label for='s'>Share key profile updates</label>"
    "<input id='s' type='checkbox' role='switch' checked data-view-name='settings-toggle'>"
    "<div data-member-name='" + INVENTED_NAME + "' componentkey='" + _digits(9) + "'>Show all</div>"
    "</main></body></html>"
)


def test_a_skeleton_names_nobody() -> None:
    skeleton = harness.skeleton_of(PEOPLE_PAGE, KEY)
    for planted in (INVENTED_NAME, "Dara", "Whitfield", SYNTHETIC_SLUG, _digits(19), _digits(12),
                    _digits(9), "secret", "fs_miniProfile%3A"):
        assert planted not in skeleton, planted


def test_a_skeleton_keeps_what_a_readers_selectors_need() -> None:
    skeleton = harness.skeleton_of(PEOPLE_PAGE, KEY)
    for kept in ('class="msg-conversation-listitem"', 'role="switch"', 'aria-expanded="false"',
                 'aria-pressed="false"', 'aria-label="Star conversation"', "\nShow all\n", "\nMe\n",
                 "\nShare key profile updates\n", 'data-test-hook="UNREAD"', 'data-view-name="settings-toggle"',
                 "https://www.linkedin.com/in/", "?miniProfileUrn=", "/feed/update/urn:li:activity:"):
        assert kept in skeleton, kept
    label_for = harness.value_shape("s", KEY)
    assert skeleton.count(label_for) == 2, "a label no longer finds its control"


async def test_a_skeleton_still_parses_and_the_setting_reader_still_reads_it(browser_page) -> None:
    """THE PROPERTY THE SKELETON EXISTS FOR, shown on the (b) reader itself:
    the switch is found by its label -- a furniture word -- through a
    for/id pair both shaped with one key, and its state survives."""
    await browser_page.set_content(harness.skeleton_of(PEOPLE_PAGE, KEY))
    assert await browser_page.locator("li.msg-conversation-listitem").count() == 1
    reading = await profile_editor.read_account_share_updates(browser_page)
    assert reading["reading"] == "on" and reading["named"] == 1


def test_a_reduced_envelope_keeps_the_evidence_and_shapes_the_rest() -> None:
    urn_key = "urn:li:activity:" + _digits(19)
    envelope = {
        "ok": True, "rows_rendered": 3, "refused": "not_self_profile",
        "results": [{"text": INVENTED_NAME + " invited you to connect", "link": "/in/" + SYNTHETIC_SLUG}],
        "company_id": {"company_id": _digits(7, "5"), "name": INVENTED_NAME},
        "anchors_per_item": {urn_key: 2},
        "read_indicator": {"state": "drawn"},
    }
    reduced = harness.reduce_envelope(envelope, KEY)
    rendered = json.dumps(reduced)
    assert INVENTED_NAME not in rendered and SYNTHETIC_SLUG not in rendered and _digits(19) not in rendered
    assert reduced["ok"] is True and reduced["rows_rendered"] == 3
    assert reduced["refused"] == "not_self_profile" and reduced["read_indicator"]["state"] == "drawn"
    assert reduced["company_id"]["company_id"] == _digits(7, "5")
    assert reduced["anchors_per_item"] == {"_withheld_keys": 1}


# --------------------------------------------------------------------------
# The pure readers.
# --------------------------------------------------------------------------


def test_an_item_record_keeps_closed_words_only() -> None:
    record = harness.item_record({
        "tag": "div", "role": "menuitem", "aria": ["aria-hidden", "data-x", "aria-" + "x" * 40],
        "view": "profile-save-to-pdf", "componentkey": True, "href": False, "button": True,
        "word": "Save to PDF", "save_to_pdf": True, "needles": [True, False],
    })
    assert record == {
        "tag": "div", "role": "menuitem", "aria_attributes": ["aria-hidden"],
        "view": "profile-save-to-pdf", "componentkey": True, "href": False, "button": True,
        "word": "Save to PDF", "save_to_pdf": True, "needles": [True, False],
    }
    odd = harness.item_record({"tag": "section", "role": "tab", "view": SYNTHETIC_SLUG,
                               "word": INVENTED_NAME})
    assert odd["tag"] == "other" and odd["role"] == "other"
    assert odd["view"] == "other" and odd["word"] is None


def test_the_save_to_pdf_handle_needs_exactly_one_item() -> None:
    one = harness.item_record({"tag": "div", "role": "menuitem", "save_to_pdf": True})
    other = harness.item_record({"tag": "div", "role": "menuitem"})
    assert harness.handle_signature([one, other]) is not None
    assert harness.handle_signature([other]) is None
    assert harness.handle_signature([one, one]) is None


def test_the_first_read_row_skips_placeholders_and_unread_rows() -> None:
    listing = {"rows": [
        {"position": 1, "rendered": False, "unread": None},
        {"position": 2, "rendered": True, "unread": True},
        {"position": 3, "rendered": True, "unread": False},
    ]}
    assert harness.first_read_row(listing) == 3
    assert harness.first_read_row({"rows": listing["rows"][:2]}) is None
    assert harness.first_read_row(None) is None


# --------------------------------------------------------------------------
# The tracked copy: what a committed fixture of this session may hold.
# --------------------------------------------------------------------------


def _member_page(name: str) -> str:
    return ("<!doctype html><html><body><main><p>" + name + "</p>"
            "<a href='https://www.linkedin.com/in/" + SYNTHETIC_SLUG + "/'>" + name + "</a>"
            "<span>Show all</span></main></body></html>")


def test_each_session_has_its_own_directory_and_a_bad_name_is_refused() -> None:
    """Forty loads a SESSION: session 3's ledger, lock, key and captures live in
    their own directory, named by LIVE_LANE_SESSION_DIR, and only a closed
    shape is taken -- a path with a separator would put state outside _state."""
    import os
    import subprocess

    assert harness.SESSION_DIR == "live2" and harness.STATE.name == "live2"
    code = "import sys; sys.path.insert(0, 'scripts'); import _probe_live_lane_session_2 as h; print(h.STATE.name)"
    for value, ok in (("live3", True), ("../x", False), ("live", False), ("live123", False)):
        env = dict(os.environ, LIVE_LANE_SESSION_DIR=value)
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), env=env,
                              capture_output=True, text=True, timeout=120)
        assert (proc.returncode == 0) is ok, (value, proc.returncode)
        if ok:
            assert proc.stdout.strip().endswith(value)


def test_a_new_ledger_names_the_session_whose_directory_it_is_in() -> None:
    """Session 3's ledger was headed "live-lane-session-2": the label was a
    constant the per-session directory never reached. A directory no session
    has used, so the ledger read is the one a first load would write; reading
    it creates nothing."""
    import os
    import subprocess

    code = ("import sys; sys.path.insert(0, 'scripts'); import _probe_live_lane_session_2 as h; "
            "print(h.LEDGER.exists(), h._ledger_read()['session'])")
    env = dict(os.environ, LIVE_LANE_SESSION_DIR="live97")
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), env=env,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-400:]
    assert proc.stdout.split() == ["False", "live97"], proc.stdout
    assert not (ROOT / "_state" / "live97").exists()


def test_a_tracked_copy_carries_no_keyed_hash_and_no_length() -> None:
    skeleton = harness.skeleton_of(_member_page(INVENTED_NAME), KEY)
    assert harness._KEYED_SHAPE.search(skeleton), "the control: the skeleton is keyed"
    copy = harness.tracked_copy(skeleton)
    assert not harness._KEYED_SHAPE.search(copy)
    assert INVENTED_NAME not in copy and SYNTHETIC_SLUG not in copy
    assert "\nx\n" in copy, "a text node is one x, whatever its length"
    assert "https://www.linkedin.com/in/x/" in copy
    assert "\nShow all\n" in copy, "LinkedIn's own words stay"
    assert copy.isascii()


def test_a_tracked_copy_passes_the_people_guard_its_keyed_skeleton_fails() -> None:
    """The reason the copy exists: a keyed shape in a member link is a
    candidate the fixture guard convicts; one x is a value reduced to shape."""
    from tests.test_fixtures_hold_only_synthetic_people import (
        ACCEPTED, PLANTED, PLANTED_PATH, violations)

    skeleton = harness.skeleton_of(_member_page(PLANTED), KEY)
    assert len(violations(PLANTED_PATH, skeleton, ACCEPTED)) == 1
    assert violations(PLANTED_PATH, harness.tracked_copy(skeleton), ACCEPTED) == []


async def test_a_tracked_copy_keeps_a_label_on_its_control(browser_page) -> None:
    page = ("<!doctype html><html><body><main><div id='autoPrefs' aria-hidden='true'>"
            "<p>Share key profile updates</p></div><span aria-hidden='true'>Off</span>"
            "<input type='checkbox' role='switch' aria-labelledby='autoPrefs'>"
            "<label for='other'>" + INVENTED_NAME + "</label><input id='other' type='checkbox'>"
            "</main></body></html>")
    copy = harness.tracked_copy(harness.skeleton_of(page, KEY))
    assert "autoPrefs" not in copy
    await browser_page.set_content(copy)
    named = browser_page.get_by_role("switch", name="Share key profile updates", exact=True)
    assert await named.count() == 1
    assert await browser_page.get_by_role("checkbox", name="x", exact=True).count() == 1


def test_a_non_ascii_word_survives_the_copy_as_a_reference() -> None:
    ellipsis = "Write a message" + chr(0x2026)
    copy = harness.tracked_copy(harness.skeleton_of("<main><p>" + ellipsis + "</p></main>", KEY))
    assert copy.isascii() and "Write a message&#8230;" in copy


#: Each session's tracked copies, by directory: session 2's 27 skeletons and
#: his settings page; session 3's 13 and the same page again; session 4's 4
#: and session 5's 1 (no settings page was read raw in either).
#: `live8` (lane U, 2026-10-10): ONE copy, the messaging page's new-message
#: composer from session 8's `lk_thread` load, written NOT by
#: `--export-fixtures` but by `scripts/_build_live8_composer_fixture.py`
#: through this harness's own `tracked_copy`, after putting back the two
#: `accept` declarations recorded live on 2026-09-05 where the skeleton's
#: shape of each matched exactly. The same checks below hold for it.
#: AND SIX MORE (the live lane, after session 9): the skeletons lane K's
#: ledger planned as tracked fixtures (its section 12.7), copied by
#: ``tracked_copy`` under the names that plan gave them -- seven in all.
#: AND live1 (lane B3, 2026-10-10): session 1's articles list and per-post
#: analytics page, built by ``scripts/_build_live1_l1_fixtures.py`` through
#: the same ``skeleton_of`` and ``tracked_copy`` -- two.
#: `live7` (lane B1, 2026-10-10): ONE copy, his intro editor from session 7's
#: load, written by `scripts/_build_intro_editor_live7_fixture.py` through this
#: harness's own `tracked_copy`, after putting back LinkedIn's labels and option
#: words where the skeleton's shape of each matched exactly under the session's
#: key, and inventing the organization and school options.
#: `live1` (lane B1, 2026-10-10): session 1's analytics pages, each written by
#: its own builder through this harness's own `skeleton_of` and `tracked_copy`:
#: the hub (`scripts/_build_dashboard_fixture.py`) and the audience page
#: (`scripts/_build_audience_fixture.py`).
#: MEASURED AT INTEGRATION 2'S MERGE OF LANE B1 (2026-11-24), the *.html count
#: of each directory on disk, never summed: `live1` 5 -- lane B3's two, lane
#: B1's two, and J 110's Home-view skeleton (merge 1), which its branch never
#: counted; `live2` 29 -- J 108's People-tab capture (merge 2) beside the 28;
#: `live9` 1 -- J 110's Posts-view skeleton, a directory its branch created
#: and never listed; `live7` 1, lane B1's. Lane B3's and lane B1's `"live1": 2`
#: were two different pairs that git merged as one equal edit.
#: `live2` 30 ON LANE BUILD-JMN26 (2026-11-25), the count on disk: J 31's
#: search with its alert toggle's one word written by keyed shape
#: (`scripts/_build_search_alert_skeleton.py`), beside the 29.
#: `live11` (the live lane, session 11, 2026-11-26): 48 copies of that session's
#: capture skeletons and their open states, each through this harness's own
#: `tracked_copy`; the runner's diagnostic skeletons stayed in gitignored state.
#: Both kept AT INTEGRATION 3'S FIFTH MERGE (2026-11-26), each re-counted on the
#: merged tree's disk: live2 30, live11 48.
#: `live11` 53 ON LANE READERS-JOBS26 (2026-11-26), the count on disk: the
#: lane's five word skeletons (`scripts/_build_live11_word_skeletons.py`, each
#: the committed copy with LinkedIn's words written where their keyed shapes
#: matched), beside the 48.
#: `live11` 49 ON LANE READERS-MSG26 (2026-11-26), the count on disk: M C93's
#: content search with its measured words kept by keyed shape and its people
#: synthetic (`scripts/_build_content_search_skeleton.py`), beside the 48.
#: Both kept AT INTEGRATION 4'S MERGE OF LANE READERS-MSG26 (2026-11-26),
#: re-counted on the merged tree's disk: live11 54 (the 48, readers-jobs26's five
#: word skeletons and readers-msg26's content search).
LIVE_FIXTURE_COUNTS = {"live1": 5, "live2": 30, "live3": 14, "live4": 4, "live5": 1, "live7": 1, "live8": 7, "live9": 1,
                       "live11": 54}


@pytest.mark.parametrize("session_dir", sorted(LIVE_FIXTURE_COUNTS))
def test_every_committed_session_fixture_is_a_tracked_copy(session_dir: str) -> None:
    """What ``--export-fixtures`` wrote, and nothing written another way: no
    keyed shape, strict ASCII, one file per skeleton plus his settings page."""
    copies = sorted((ROOT / "tests" / "fixtures" / session_dir).glob("*.html"))
    assert len(copies) == LIVE_FIXTURE_COUNTS[session_dir], [p.name for p in copies]
    for path in copies:
        text = path.read_bytes().decode("ascii")
        assert not harness._KEYED_SHAPE.search(text), path.name
        assert text.startswith("<!doctype html>"), path.name


def test_every_session_fixture_directory_is_counted() -> None:
    """A session directory nobody added to the table would pass unread."""
    found = sorted(p.name for p in (ROOT / "tests" / "fixtures").glob("live*") if p.is_dir())
    assert found == sorted(LIVE_FIXTURE_COUNTS), found


def test_closed_again_means_the_menus_own_words_are_gone_and_the_trigger_reads_as_before() -> None:
    before = {"More": 1}
    added = {"Save to PDF": 1}
    assert harness.closed_again(added, {"More": 1}, before, "false", "false")
    assert harness.closed_again(added, {"More": 1, "Share": 1}, before, "false", "false"), (
        "a word that appears for another reason -- a focus tooltip -- is not the menu")
    assert not harness.closed_again(added, {"More": 1, "Save to PDF": 1}, before, "false", "false")
    assert not harness.closed_again(added, {"More": 1}, before, "true", "false")


def test_an_expanded_control_is_read_by_structure() -> None:
    row = harness.expanded_record({"tag": "button", "type_button": True, "href": False,
                                   "haspopup": INVENTED_NAME, "svg": True, "more": True})
    assert row == {"tag": "button", "type_button": True, "href": False, "haspopup": "other",
                   "svg": True, "more": True}


# --------------------------------------------------------------------------
# The press flow, end to end, in a local headless Chromium.
# --------------------------------------------------------------------------


def _menu_page(*, closes: bool = True, opens_a_conversation: bool = False) -> str:
    escape = ("t.setAttribute('aria-expanded','false'); m.innerHTML='';" if closes else "")
    opened = ("document.getElementById('list').innerHTML='<li class=\"msg-s-message-list__event\"></li>';"
              if opens_a_conversation else "")
    return (
        "<!doctype html><html><body><main><ul id='list'></ul><div class='artdeco-dropdown'>"
        "<button id='t' type='button' aria-label='More' aria-expanded='false' aria-controls='m'>More</button>"
        "<div id='m' class='artdeco-dropdown__content'></div></div></main><script>"
        "const t=document.getElementById('t'), m=document.getElementById('m');"
        "t.addEventListener('click',()=>{t.setAttribute('aria-expanded','true');" + opened +
        "m.innerHTML='<div role=\"menuitem\" data-view-name=\"profile-save-to-pdf\">Save to PDF</div>"
        "<div role=\"menuitem\">Copy link to profile</div><div role=\"menuitem\">" + INVENTED_NAME + "</div>';});"
        "document.addEventListener('keydown',(e)=>{if(e.key==='Escape'){" + escape + "}});"
        "</script></body></html>"
    )


@pytest.fixture()
def quick(tmp_path, monkeypatch):
    monkeypatch.setattr(harness.s1, "OPEN_SETTLE_S", 0.05)
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "SHAPE_KEY_FILE", tmp_path / "shape.key")
    return tmp_path


#: THE HANDLE SESSION 2 USED FOR THE MORE, page-wide and blind to drawing.
#: Kept here for two jobs: finding the synthetic menu's trigger in the press
#: tests below, and showing on today's skeletons what it took.
OLD_MORE_HANDLE = 'main button[aria-label="More"][aria-expanded="false"]'


async def test_one_press_is_read_by_attribute_and_closed_again(browser_page, quick) -> None:
    await browser_page.set_content(_menu_page())
    handle, count = await harness._one_handle(browser_page.locator(OLD_MORE_HANDLE))
    assert count == 1
    result = await harness.press_and_read(browser_page, "in_me_more", handle, True,
                                          needles=harness.N76_NEEDLES)
    assert result["pressed"] and result["container_found"] and result["closed_again"]
    assert [item["save_to_pdf"] for item in result["items"]] == [True, False, False]
    assert [item["word"] for item in result["items"]] == ["Save to PDF", "Copy link to profile", None]
    assert result["items"][1]["needles"] == [True, False, False, False]
    assert result["items"][0]["view"] == "profile-save-to-pdf"
    assert result["words_added"] == {"Copy link to profile": 1, "Save to PDF": 1}
    assert harness.handle_signature(result["items"]) is not None
    written = (quick / "in_me_more-open.skeleton.html").read_text(encoding="utf-8")
    assert INVENTED_NAME not in written and "Save to PDF" in written
    assert INVENTED_NAME not in json.dumps(result)


async def test_a_menu_that_stays_open_stops_the_session(browser_page, quick) -> None:
    await browser_page.set_content(_menu_page(closes=False))
    handle, _count = await harness._one_handle(browser_page.locator(OLD_MORE_HANDLE))
    with pytest.raises(harness._Anomaly) as stop:
        await harness.press_and_read(browser_page, "in_me_more", handle, False)
    assert stop.value.kind == "the_menu_did_not_close"


async def test_a_conversation_opened_by_a_press_stops_the_session(browser_page, quick) -> None:
    await browser_page.set_content(_menu_page(opens_a_conversation=True))
    handle, _count = await harness._one_handle(browser_page.locator(OLD_MORE_HANDLE))
    with pytest.raises(harness._Anomaly) as stop:
        await harness.press_and_read(browser_page, "compose_c9", handle, False, messaging=True)
    assert stop.value.kind == "a_conversation_opened"


async def test_our_words_are_the_only_keys_that_come_back(browser_page) -> None:
    await browser_page.set_content(
        "<main><span>Show all</span><span>" + INVENTED_NAME + "</span>"
        "<button aria-label='Star conversation'></button><span hidden>Save to PDF</span></main>")
    counted = await harness.furniture_counts(browser_page)
    assert counted == {"Show all": 1, "aria:Star conversation": 1}


# --------------------------------------------------------------------------
# D-1, fix 3: the top card's More, on today's skeletons of both profiles.
# --------------------------------------------------------------------------

LIVE2 = ROOT / "tests" / "fixtures" / "live2"

#: A landing the press gate reads as his own profile (``press.self_landing``),
#: on an invented slug; served by the test page's own route, never fetched.
PROFILE_URL = "https://www.linkedin.com/in/xxxx/?isSelfProfile=true"

#: LINKEDIN'S STYLESHEET, WHICH NO SKELETON CARRIES, STOOD IN FOR BY ONE RULE:
#: the action bar the page does not show at the width in question. Each class
#: sits on exactly one element of both skeletons -- that bar's own container.
#: WIDE is his window on 2026-09-28: the bar holding the LABELLED More was not
#: drawn -- its More never became actionable, twice, with the window in front
#: (DERIVED from those two timeouts). NARROW hides the other bar instead.
WIDE = "._2f3017c2 { display: none !important; }"
NARROW = "._53a77971 { display: none !important; }"


async def _serve_profile(page, name: str, hide: str) -> None:
    body = (LIVE2 / (name + ".html")).read_text(encoding="ascii")

    async def handler(route) -> None:  # noqa: ANN001 - playwright route
        if route.request.url == PROFILE_URL:
            await route.fulfill(status=200, content_type="text/html", body=body)
        else:
            await route.abort()

    await page.route("**/*", handler)
    await page.goto(PROFILE_URL, wait_until="domcontentloaded")
    if hide:
        await page.add_style_tag(content=hide)


class _ServedBrowser:
    """``BROWSER.session()`` over one test page, and nothing else."""

    def __init__(self, page) -> None:  # noqa: ANN001 - playwright page
        self.page = page

    @contextlib.asynccontextmanager
    async def session(self):
        yield self.page


async def test_d1_the_top_card_is_the_section_around_the_first_h2(browser_page) -> None:
    """Both profiles: the top card holds both action bars -- on his, two of
    "Open to" and of "Enhance profile", one More and one Resources; on the
    first-degree profile's, two More -- and its first h2 is the page's first."""
    await _serve_profile(browser_page, "in_me", "")
    card = harness.topcard_of(browser_page)
    assert await card.count() == 1
    drawn = {word: await card.get_by_role("button", name=word, exact=True, include_hidden=True).count()
             for word in harness.TOPCARD_WORDS}
    assert drawn == {"More": 1, "Resources": 1, "Open to": 2, "Enhance profile": 2,
                     "Add profile section": 0}
    await _serve_profile(browser_page, "first_degree_profile", "")
    card = harness.topcard_of(browser_page)
    assert await card.get_by_role("button", name="More", exact=True, include_hidden=True).count() == 2


async def test_d1_the_old_handle_takes_the_hidden_more_on_both_profiles(browser_page) -> None:
    """THE DEFECT, measured on today's skeletons at his width: the old handle
    finds exactly one More on each profile -- the labelled one, in the bar the
    page does not show -- so "exactly one" was true and the one was not drawn.
    On the first-degree profile a visible More sat beside it, labelled by text."""
    for name in ("in_me", "first_degree_profile"):
        await _serve_profile(browser_page, name, WIDE)
        old = browser_page.locator(OLD_MORE_HANDLE)
        assert await old.count() == 1, name
        assert not await old.is_visible(), name


_COUNT_CLICKS = """
() => { window.__clicks = 0;
        document.addEventListener('click', () => { window.__clicks += 1; }, true); }
"""


@pytest.mark.parametrize("width,opener", [(WIDE, "Resources"), (NARROW, "More")])
async def test_d1_the_key_presses_the_one_opener_his_width_draws(
        browser_page, quick, monkeypatch, width, opener) -> None:
    """FIX 3, END TO END, AND THE ORCHESTRATOR'S RULING OF 2026-09-28 12:42:
    press the opener the top card DRAWS -- at his width Resources, at the
    narrow one More -- ONCE. Red before fix 3: the key took the old handle's
    one match and its click waited out Playwright's actionability check on a
    control that is not drawn (TimeoutError), as it did live."""
    await _serve_profile(browser_page, "in_me", width)
    await browser_page.evaluate(_COUNT_CLICKS)
    monkeypatch.setattr(harness, "BROWSER", _ServedBrowser(browser_page))
    result = await harness._in_me_more(False)
    assert result["opener"] == opener
    assert result["counts"][opener][1] == 1
    assert result["opening"]["pressed"] is True and result["opening"]["closed_again"] is True
    assert await browser_page.evaluate("window.__clicks") == 1, "one press, and only one"


@pytest.mark.parametrize("profile,hide", [("in_me", ""), ("first_degree_profile", "")])
async def test_d1_neither_or_both_openers_visible_refuses(
        browser_page, quick, monkeypatch, profile, hide) -> None:
    """With no stylesheet both bars show: his profile then draws More AND
    Resources visible, the first-degree profile's two Mores -- not exactly one opener, so
    nothing is pressed."""
    await _serve_profile(browser_page, profile, hide)
    await browser_page.evaluate(_COUNT_CLICKS)
    monkeypatch.setattr(harness, "BROWSER", _ServedBrowser(browser_page))
    result = await harness._in_me_more(False)
    assert result["stopped"] == "opener_not_exactly_one"
    assert await browser_page.evaluate("window.__clicks") == 0


async def test_a_menu_drawn_as_a_role_menu_elsewhere_is_read(browser_page, quick) -> None:
    """THE NEW MARKUP'S MENU: no artdeco dropdown and no aria-controls, a
    role=menu drawn apart from its trigger. The one visible role=menu is the
    container, and Save to PDF is found by comparison inside the page."""
    await browser_page.set_content(
        "<!doctype html><html><body><main><button id='t' type='button' aria-label='More' "
        "aria-expanded='false'>More</button></main><div id='portal'></div><script>"
        "const t=document.getElementById('t'), p=document.getElementById('portal');"
        "t.addEventListener('click',()=>{t.setAttribute('aria-expanded','true');"
        "p.innerHTML='<div role=\"menu\"><div role=\"menuitem\">Save to PDF</div>"
        "<div role=\"menuitem\">" + INVENTED_NAME + "</div></div>';});"
        "document.addEventListener('keydown',(e)=>{if(e.key==='Escape'){"
        "t.setAttribute('aria-expanded','false'); p.innerHTML='';}});"
        "</script></body></html>")
    handle, _count = await harness._one_handle(browser_page.locator(OLD_MORE_HANDLE))
    result = await harness.press_and_read(browser_page, "in_me_more", handle, False)
    assert result["container_found"] is True
    assert [item["save_to_pdf"] for item in result["items"]] == [True, False]
    assert result["closed_again"] is True and result["closed_by"] == "escape"


async def test_d1_the_new_handle_takes_the_one_visible_more(browser_page) -> None:
    """The first-degree profile at the same width: 2 drawn, 1 visible, and the
    one taken is the text-labelled More the old handle never matched. His
    own at the narrow width: his labelled More, visible, taken."""
    await _serve_profile(browser_page, "first_degree_profile", WIDE)
    handle, drawn, visible = await harness.topcard_control(browser_page, harness.MORE_NAME)
    assert (drawn, visible) == (2, 1)
    assert await handle.get_attribute("aria-label") is None
    assert await handle.is_visible()
    await _serve_profile(browser_page, "in_me", NARROW)
    handle, drawn, visible = await harness.topcard_control(browser_page, harness.MORE_NAME)
    assert (drawn, visible) == (1, 1)
    assert await handle.get_attribute("aria-label") == "More"


async def test_d1_his_wide_top_card_shows_resources_where_the_other_bar_has_more(browser_page) -> None:
    """What session 3 must rule on before D-1 can fire at his width: the bar
    his window shows holds "Resources" and no More. Counted, never pressed."""
    await _serve_profile(browser_page, "in_me", WIDE)
    counts = {}
    for word in ("More", "Resources"):
        _handle, drawn, visible = await harness.topcard_control(browser_page, word)
        counts[word] = (drawn, visible)
    assert counts == {"More": (1, 0), "Resources": (1, 1)}


async def test_d1_two_visible_refuse(browser_page) -> None:
    """With no stylesheet both bars show, and the first-degree profile's two More are both
    visible: exactly one is required, so none is taken."""
    await _serve_profile(browser_page, "first_degree_profile", "")
    handle, drawn, visible = await harness.topcard_control(browser_page, harness.MORE_NAME)
    assert (handle, drawn, visible) == (None, 2, 2)


# --------------------------------------------------------------------------
# C8, fix 4: the folder menu's close step, on today's skeleton of it open.
# --------------------------------------------------------------------------

#: THE FOLDER MENU'S BEHAVIOUR, which a skeleton cannot carry, installed on
#: today's skeleton of the composer with that menu open. The skeleton shows
#: the structure: an artdeco dropdown -- its trigger the folder pill,
#: aria-expanded "true" while open; its content a sibling holding four items
#: (Focused, Other, Archived, Spam), each a folder CHOICE; NO close control of
#: its own. The model starts it CLOSED, and then: Escape does what it did live
#: on 2026-09-28, per ``escape`` ("none": nothing; "closes": closes;
#: "collapses": the trigger reads closed while the items stay drawn); a click
#: on the trigger toggles it, as an artdeco dropdown's trigger does (ASSUMED
#: from the component, never yet pressed live), unless ``toggles`` is False.
#: Every trigger click is counted.
_C8_MODEL = """
([escape, toggles]) => {
  const t = document.querySelector('[data-test-messaging-inbox-filters__folder-pill]');
  const box = t.closest('.artdeco-dropdown').querySelector('.artdeco-dropdown__content');
  window.__clicks = 0;
  const set = (open) => {
    t.setAttribute('aria-expanded', open ? 'true' : 'false');
    box.classList.toggle('artdeco-dropdown__content--is-open', open);
    box.style.display = open ? '' : 'none';
  };
  set(false);
  t.addEventListener('click', () => {
    window.__clicks += 1;
    if (window.__clicks === 1 || toggles) set(t.getAttribute('aria-expanded') !== 'true');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (escape === 'closes') set(false);
    if (escape === 'collapses') t.setAttribute('aria-expanded', 'false');
  });
}
"""


async def _c8_world(page, escape: str, toggles: bool = True) -> object:
    body = (LIVE2 / "compose_c8-open.html").read_text(encoding="ascii")

    async def handler(route) -> None:  # noqa: ANN001 - playwright route
        if route.request.url == harness.COMPOSE_URL:
            await route.fulfill(status=200, content_type="text/html", body=body)
        else:
            await route.abort()

    await page.route("**/*", handler)
    await page.goto(harness.COMPOSE_URL, wait_until="domcontentloaded")
    await page.evaluate(_C8_MODEL, [escape, toggles])
    handle, count = await harness._one_handle(
        page.locator(harness.FOLDER_TRIGGER).filter(has_text="Focused"))
    assert count == 1, "the harness's own C8 trigger, exactly one on today's skeleton"
    return handle


async def test_c8_the_menu_escape_left_open_is_closed_by_its_own_trigger(browser_page, quick) -> None:
    """FIX 4, AS IT HAPPENED LIVE. Red before the fix: the press opened the
    menu, Escape left it open, and the key stopped as an anomaly -- the
    session's own outcome. Now the close step presses the SAME trigger once
    more, only because it still reads expanded, and the menu closes."""
    handle = await _c8_world(browser_page, "none")
    result = await harness.press_and_read(browser_page, "compose_c8", handle, False, messaging=True)
    assert result["closed_again"] is True
    assert result["closed_by"] == "trigger"
    assert result["container_found"] is True and len(result["items"]) == 4
    assert [item["word"] for item in result["items"]] == ["Focused", "Other", "Archived", "Spam"]
    assert result["message_events"] == [0, 0, 0]
    assert await browser_page.evaluate("window.__clicks") == 2


async def test_c8_a_menu_escape_closes_is_pressed_once(browser_page, quick) -> None:
    handle = await _c8_world(browser_page, "closes")
    result = await harness.press_and_read(browser_page, "compose_c8", handle, False, messaging=True)
    assert (result["closed_again"], result["closed_by"]) == (True, "escape")
    assert await browser_page.evaluate("window.__clicks") == 1


async def test_c8_a_menu_nothing_closes_still_stops_the_session(browser_page, quick) -> None:
    """The close step is ONE more press, never a loop, and it masks nothing: a
    menu that stays open after it is the same anomaly as before."""
    handle = await _c8_world(browser_page, "none", toggles=False)
    with pytest.raises(harness._Anomaly) as stop:
        await harness.press_and_read(browser_page, "compose_c8", handle, False, messaging=True)
    assert stop.value.kind == "the_menu_did_not_close"
    assert await browser_page.evaluate("window.__clicks") == 2


async def test_c8_a_trigger_reading_closed_is_never_pressed_again(browser_page, quick) -> None:
    """When Escape leaves the trigger reading closed while the words stay
    drawn, a second click would OPEN the menu: it is not made, and the
    anomaly stands."""
    handle = await _c8_world(browser_page, "collapses")
    with pytest.raises(harness._Anomaly) as stop:
        await harness.press_and_read(browser_page, "compose_c8", handle, False, messaging=True)
    assert stop.value.kind == "the_menu_did_not_close"
    assert await browser_page.evaluate("window.__clicks") == 1


# --------------------------------------------------------------------------
# The setting, and its offline check.
# --------------------------------------------------------------------------


async def test_the_restated_locator_agrees_with_the_reader_on_every_b_world(browser_page) -> None:
    from tests.test_account_share_updates import WORLDS

    for name, (_want, world) in WORLDS.items():
        await browser_page.set_content(world)
        reading = await profile_editor.read_account_share_updates(browser_page)
        restated = await harness.named_setting_control(browser_page).count()
        assert restated == reading["named"], name


PROPERTY_ONLY = (
    "<!doctype html><html><body><main><label for='s'>" + profile_editor.ACCOUNT_SETTING_NAME + "</label>"
    "<input id='s' type='checkbox' role='switch'></main>"
    "<script>document.getElementById('s').checked = true;</script></body></html>"
)
ATTRIBUTE_ON = (
    "<!doctype html><html><body><main><label for='s'>" + profile_editor.ACCOUNT_SETTING_NAME + "</label>"
    "<input id='s' type='checkbox' role='switch' checked></main></body></html>"
)


async def _live(page, world: str) -> dict:
    await page.set_content(world)
    reading = await profile_editor.read_account_share_updates(page)
    return {"served": True, **{k: reading.get(k) for k in ("reading", "named", "input", "aria")},
            **(await harness.state_in_markup(page)), "captured": await page.content()}


async def test_a_state_in_the_markup_replays_and_agrees(browser_page) -> None:
    live = await _live(browser_page, ATTRIBUTE_ON)
    assert live["reading"] == "on" and live["checked_attribute"] == 1
    offline = await harness.replay_reading(live["captured"])
    assert harness.offline_verdict(live, offline) == "AGREES"


async def test_a_state_held_only_in_the_property_is_named_not_trusted(browser_page) -> None:
    """THE CASE A CAPTURE CANNOT ANSWER, reproduced: the live reader reads
    ON through the checked PROPERTY, the capture carries no checked
    attribute, and its replay reads OFF. The verdict says why, and it is not
    AGREES -- so it cannot release the six edits by itself."""
    live = await _live(browser_page, PROPERTY_ONLY)
    assert live["reading"] == "on"
    assert (live["checked_property"], live["checked_attribute"]) == (1, 0)
    offline = await harness.replay_reading(live["captured"])
    assert offline["reading"] == "off"
    assert harness.offline_verdict(live, offline) == "STATE-NOT-IN-MARKUP"


_LIVE = {"served": True, "reading": "off", "named": 1, "input": 1, "aria": None,
         "checked_property": 0, "checked_attribute": 0}
_OFFLINE = {"reading": "off", "named": 1, "input": 1, "aria": None}


@pytest.mark.parametrize("live,offline,verdict", [
    (_LIVE, _OFFLINE, "AGREES"),
    (dict(_LIVE, served=False), _OFFLINE, "NO-LIVE-READING"),
    (None, _OFFLINE, "NO-LIVE-READING"),
    (dict(_LIVE, reading="unknown"), _OFFLINE, "LIVE-UNKNOWN"),
    (_LIVE, None, "NO-OFFLINE-READING"),
    (_LIVE, dict(_OFFLINE, named=0), "STRUCTURE-DIFFERS"),
    (_LIVE, dict(_OFFLINE, input=0), "STRUCTURE-DIFFERS"),
    (dict(_LIVE, checked_property=1), _OFFLINE, "STATE-NOT-IN-MARKUP"),
    (_LIVE, dict(_OFFLINE, reading="on"), "DISAGREES"),
])
def test_every_offline_verdict(live, offline, verdict) -> None:
    assert harness.offline_verdict(live, offline) == verdict


# --------------------------------------------------------------------------
# Lane D's LQ-4: only the download-behaviour lines survive.
# --------------------------------------------------------------------------

_DECOY_TITLE = "Inbox of " + INVENTED_NAME
_DECOY_URL = "https://www.linkedin.com/in/" + SYNTHETIC_SLUG + "/"


def _log(first="allowAndName", second="default", error_on=None) -> list[str]:
    lines = [
        'pw:protocol SEND {"id":1,"method":"Target.setDiscoverTargets","params":{"discover":true}}',
        'pw:protocol RECV {"method":"Target.targetCreated","params":{"targetInfo":{"id":1,'
        '"title":"' + _DECOY_TITLE + '","url":"' + _DECOY_URL + '"}}}',
        'pw:protocol SEND {"id":7,"method":"Browser.setDownloadBehavior","params":{"behavior":"'
        + first + '","downloadPath":"C:/tmp/playwright-artifacts-x","eventsEnabled":true}}',
        'pw:protocol RECV {"id":7,"result":{}}',
        'pw:protocol RECV {"id":1,"result":{"targetInfos":[{"title":"' + _DECOY_TITLE + '"}]}}',
        'pw:protocol SEND {"id":9,"method":"Browser.setDownloadBehavior","sessionId":"S",'
        '"params":{"behavior":"' + second + '"}}',
        'pw:protocol RECV {"id":9,' + ('"error":{"code":-1}' if error_on == 9 else '"result":{}') + "}",
    ]
    return lines


def test_the_filter_keeps_the_two_sends_and_their_answers_and_nothing_else() -> None:
    events = harness.protocol_events(_log())
    assert [(e["direction"], e.get("behavior") or e.get("answers")) for e in events] == [
        ("send", "allowAndName"), ("answer", "allowAndName"), ("send", "default"), ("answer", "default")]
    rendered = json.dumps(events)
    for decoy in (INVENTED_NAME, SYNTHETIC_SLUG, "playwright-artifacts", "C:/tmp"):
        assert decoy not in rendered, decoy


@pytest.mark.parametrize("events,before,during,after,restored,error,verdict", [
    (harness.protocol_events(_log()), 0, 1, 0, True, None, "PASS"),
    (harness.protocol_events(_log(first="default", second="allowAndName")), 0, 1, 0, True, None, "FAIL-ORDER"),
    (harness.protocol_events(_log(second="allowAndName")), 0, 1, 0, True, None, "FAIL-ORDER"),
    (harness.protocol_events(_log(error_on=9)), 0, 1, 0, True, None, "FAIL-ACKNOWLEDGEMENT"),
    (harness.protocol_events(_log()[:4]), 0, 1, 0, True, None, "FAIL-ORDER"),
    (harness.protocol_events(_log()), 0, 0, 0, True, None, "FAIL-FOLDER"),
    (harness.protocol_events(_log()), 1, 2, 2, True, None, "FAIL-FOLDER"),
    (harness.protocol_events(_log()), 0, 1, 0, False, "TimeoutError", "FAIL-RECORD"),
])
def test_lane_d_s_pass_rule(events, before, during, after, restored, error, verdict) -> None:
    assert harness.attach_verdict(events, before, during, after, restored, error) == verdict


# --------------------------------------------------------------------------
# Lane D's LQ-4, HERMETIC: the attach child counts in a temp directory of its
# own, so a folder another process makes or leaves in the system temp is never
# counted -- and a folder the child itself leaves still fails.
# --------------------------------------------------------------------------

#: THE STAND-IN FOR ``--attach-child``, spawned by the harness's own
#: ``_attach_check`` in place of the real child: no browser, no network, no
#: page. It waits for the test's go -- by then a FOREIGN artifacts folder sits
#: where the old count looked -- then does to a temp directory what the real
#: child's driver does: makes ONE artifacts folder in ITS
#: ``tempfile.gettempdir()``. It writes the two download-behaviour sends and
#: their answers to stderr (this file's ``_log()``, decoys and all), prints the
#: child's report line with its own count, and removes its folder unless told
#: to leave it.
_STAND_IN = """\
import json
import os
import sys
import tempfile

LINES = None
prefix, mode = sys.argv[1], sys.argv[2]
sys.stdin.readline()
own = tempfile.mkdtemp(prefix=prefix)
for line in LINES:
    sys.stderr.write(line + "\\n")
sys.stderr.flush()
during = sum(1 for name in os.listdir(tempfile.gettempdir()) if name.startswith(prefix))
print(json.dumps({"during": during, "restored": True, "error": None}), flush=True)
if mode == "clean":
    os.rmdir(own)
"""


class _StandInSpawner:
    """``harness.subprocess`` for one run: the real module in every attribute
    but ``Popen``, which spawns the stand-in in place of ``--attach-child`` --
    with the harness's own env, pipes and encoding, recorded -- and REFUSES any
    other command, so nothing real is ever spawned from these tests. While the
    stand-in runs, and before it counts, it plants a FOREIGN artifacts folder in
    ``foreign`` and leaves it there, as a concurrent suite leaves one."""

    def __init__(self, script: Path, mode: str, foreign: Path) -> None:
        self.script, self.mode, self.foreign = script, mode, foreign
        self.env: dict[str, str] = {}
        self.planted: Path | None = None

    def __getattr__(self, name: str):
        return getattr(subprocess, name)

    def Popen(self, argv, **kwargs):  # noqa: N802 -- the module's own name
        assert list(argv[-1:]) == ["--attach-child"], argv
        self.env = dict(kwargs["env"])
        child = subprocess.Popen(
            [sys.executable, str(self.script), harness.ARTIFACTS_PREFIX, self.mode],
            stdin=subprocess.PIPE, **kwargs)
        try:
            self.planted = Path(tempfile.mkdtemp(prefix=harness.ARTIFACTS_PREFIX + "foreign-",
                                                 dir=self.foreign))
        finally:
            child.stdin.write("go\n")
            child.stdin.close()
        return child


@pytest.fixture
def attach_world(tmp_path, monkeypatch):
    """THE SYSTEM TEMP, MOVED INTO ``tmp_path``: this process's ``tempfile``
    and the environment every child inherits both point there, so the count
    the harness took before its fix reads that directory, and nothing is
    planted in, or counted from, the real one. ``STATE`` moves too. Yields the
    moved system temp and a runner: ``run(mode)`` is one ``_attach_check``."""
    system_temp = tmp_path / "system_temp"
    system_temp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(system_temp))
    for name in ("TMP", "TEMP", "TMPDIR"):
        monkeypatch.setenv(name, str(system_temp))
    monkeypatch.setattr(harness, "STATE", tmp_path / "state")
    script = tmp_path / "attach_child_stand_in.py"
    script.write_text(_STAND_IN.replace("LINES = None", "LINES = " + repr(_log())), encoding="ascii")

    def run(mode: str) -> tuple[dict, _StandInSpawner]:
        spawner = _StandInSpawner(script, mode, system_temp)
        monkeypatch.setattr(harness, "subprocess", spawner)
        return harness._attach_check(), spawner

    return system_temp, run


def test_a_folder_another_process_leaves_in_the_system_temp_is_never_counted(attach_world) -> None:
    """THE DEFECT, MEASURED LIVE 2026-09-28. A concurrent test suite made and
    removed artifacts folders in the system temp during the attach, and the
    count read [2456, 2461, 2459] -> FAIL-FOLDER on a sound attach; on a quiet
    box it read [2455, 2456, 2455] -> PASS. It could not tell its own folder
    from another process's. Here a foreign folder is planted in the (moved)
    system temp while a stand-in that cleans up after itself runs, and is left
    there: the child counts in a directory of its own, so the verdict is PASS
    and the foreign folder is still where it was put, uncounted."""
    system_temp, run = attach_world
    out, spawner = run("clean")
    assert (out["verdict"], out["artifacts"]) == ("PASS", [0, 1, 0]), out
    assert spawner.planted is not None and spawner.planted.is_dir()
    assert [p.name for p in system_temp.iterdir()] == [spawner.planted.name]
    own = harness.attach_tmp_dir().resolve()
    for name in ("TMP", "TEMP", "TMPDIR"):
        assert Path(spawner.env[name]).resolve() == own, name
    assert spawner.env["DEBUG"] == "pw:protocol"
    assert list(own.iterdir()) == []


def test_the_control_a_folder_the_child_leaves_behind_still_fails(attach_world) -> None:
    """THE CONTROL: a count that cannot fail certifies nothing. The same run,
    foreign folder and all, with a stand-in that LEAVES its own folder reads
    FAIL-FOLDER -- and the leftover sits in the child's own directory,
    attributable, while the foreign folder is still uncounted where it was
    planted."""
    system_temp, run = attach_world
    out, spawner = run("leave")
    assert (out["verdict"], out["artifacts"]) == ("FAIL-FOLDER", [0, 1, 1]), out
    left = [p.name for p in harness.attach_tmp_dir().iterdir()]
    assert len(left) == 1 and left[0].startswith(harness.ARTIFACTS_PREFIX), left
    assert [p.name for p in system_temp.iterdir()] == [spawner.planted.name]


def test_each_run_starts_from_an_empty_directory_of_its_own(attach_world) -> None:
    """A run's leftovers never reach the next run's count: a failed run leaves
    its folder, a stray file is added beside it, and the next run empties the
    directory before it counts -- so it reads from zero again, and passes when
    its own child cleans up."""
    _system_temp, run = attach_world
    assert run("leave")[0]["verdict"] == "FAIL-FOLDER"
    (harness.attach_tmp_dir() / "stray.txt").write_text("x", encoding="ascii")
    out, _spawner = run("clean")
    assert (out["verdict"], out["artifacts"]) == ("PASS", [0, 1, 0]), out
    assert list(harness.attach_tmp_dir().iterdir()) == []


def test_emptying_refuses_anything_not_under_the_sessions_own_state(tmp_path, monkeypatch) -> None:
    """Emptying deletes, so it acts only UNDER the session's own gitignored
    directory. A directory beside it, that directory itself, a ``..`` that
    climbs out of it and the directory above it are each REFUSED before
    anything is deleted -- the canary outside survives. THE CONTROL: under it,
    the directory is emptied and made."""
    state = tmp_path / "state"
    monkeypatch.setattr(harness, "STATE", state)
    outside = tmp_path / "outside"
    outside.mkdir()
    canary = outside / "canary.txt"
    canary.write_text("kept", encoding="ascii")
    for refused in (outside, state, state / ".." / "outside", tmp_path):
        with pytest.raises(ValueError):
            harness.fresh_attach_tmp(refused)
    assert canary.read_text(encoding="ascii") == "kept"
    inside = state / "attach_tmp"
    (inside / (harness.ARTIFACTS_PREFIX + "old")).mkdir(parents=True)
    (inside / "stray.txt").write_text("x", encoding="ascii")
    assert harness.fresh_attach_tmp(inside) == inside.resolve()
    assert inside.is_dir() and list(inside.iterdir()) == []


def _link_directory(link: Path, target: Path) -> None:
    """A DIRECTORY LINK at ``link`` leading to ``target``: a junction on
    Windows -- no privilege needed, and ``is_symlink()`` reads False for one --
    and a symlink elsewhere. Skips when neither can be made."""
    try:
        if sys.platform == "win32":
            import _winapi

            _winapi.CreateJunction(str(target), str(link))
        else:
            os.symlink(target, link, target_is_directory=True)
    except (OSError, AttributeError, ImportError) as exc:
        pytest.skip("no directory link can be made here: " + type(exc).__name__)


def test_a_link_that_leads_out_of_the_sessions_state_is_refused(tmp_path, monkeypatch) -> None:
    """A PATH IS NOT A PLACE. A link named ``attach_tmp`` under the session's
    directory is under it by its spelling; resolved, it leads out -- and is
    refused before anything is deleted, with the canary it leads to intact."""
    state = tmp_path / "state"
    state.mkdir()
    monkeypatch.setattr(harness, "STATE", state)
    outside = tmp_path / "outside"
    outside.mkdir()
    canary = outside / "canary.txt"
    canary.write_text("kept", encoding="ascii")
    link = state / "attach_tmp"
    _link_directory(link, outside)
    try:
        with pytest.raises(ValueError):
            harness.fresh_attach_tmp(link)
        assert canary.read_text(encoding="ascii") == "kept"
    finally:
        if sys.platform == "win32":
            os.rmdir(link)
        else:
            os.unlink(link)


class _StartAndStopOnly:
    """``BROWSER`` for the child's own count: it starts and stops, and attaches
    to nothing."""

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None


def test_the_child_counts_only_in_the_attach_directory(tmp_path, monkeypatch, capsys) -> None:
    """The parent counts in the session's attach directory; the child counts
    in ITS ``tempfile.gettempdir()``. Were those ever two directories, a child
    count from a crowded system temp beside two zeros from an empty directory
    would read as appeared-and-gone for a driver that made nothing. So the
    child reports a count only when its temp directory IS the attach
    directory, and no count otherwise -- which the rule reads as FAIL-FOLDER."""
    monkeypatch.setattr(harness, "BROWSER", _StartAndStopOnly())
    monkeypatch.setattr(harness.cdp_bridge, "LAST_DOWNLOAD_RESET", {"restored": True})
    monkeypatch.setattr(harness, "STATE", tmp_path / "state")
    own = harness.fresh_attach_tmp(harness.attach_tmp_dir())
    crowded = tmp_path / "crowded"
    (crowded / (harness.ARTIFACTS_PREFIX + "foreign")).mkdir(parents=True)
    during = {}
    for label, temp in (("own", own), ("crowded", crowded)):
        monkeypatch.setattr(tempfile, "tempdir", str(temp))
        assert asyncio.run(harness._attach_child()) == 0
        during[label] = json.loads(capsys.readouterr().out.strip().splitlines()[-1])["during"]
    assert during == {"own": 0, "crowded": None}


# --------------------------------------------------------------------------
# What the file itself does, read off its syntax tree.
# --------------------------------------------------------------------------


def _tree() -> ast.Module:
    return ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))


def _enclosing_function(tree: ast.Module, target: ast.AST) -> str:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(child is target for child in ast.walk(node)):
                return node.name
    return "<module>"


def test_every_click_is_the_triggers_own_in_press_and_read_and_every_key_press_is_escape() -> None:
    """TWO clicks, both on the one trigger, both in press_and_read: the open,
    and fix 4's close step -- which runs only inside an ``if`` that reads the
    trigger still expanded after Escape and closed before the press."""
    tree = _tree()
    clicks, keys = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "click":
                clicks.append((_enclosing_function(tree, node), ast.unparse(node.func.value)))
            if node.func.attr == "press":
                keys.append(ast.unparse(node.args[0]) if node.args else "")
    assert clicks == [("press_and_read", "handle"), ("press_and_read", "handle")], clicks
    assert keys == ["'Escape'"], keys
    guards = [ast.unparse(node.test) for node in ast.walk(tree) if isinstance(node, ast.If)
              and any(isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                      and inner.func.attr == "click" for inner in ast.walk(node))]
    assert len(guards) == 1, guards
    for condition in ("closed_by is None", "expanded_after == 'true'", "expanded_before == 'false'"):
        assert condition in guards[0], (condition, guards)


#: The tools a harness key may call: every one a read.
READ_TOOLS = {
    "linkedin_list_conversations", "linkedin_open_messaging", "linkedin_recent_job_searches",
    "linkedin_premium_job_collection", "linkedin_search_appearances", "linkedin_notifications",
    "linkedin_connections", "linkedin_job_detail", "linkedin_people_search_shape",
    "linkedin_group_memberships", "linkedin_group_page", "linkedin_open_thread",
    "linkedin_messaging_presence", "linkedin_recruiter_insights", "linkedin_search_jobs",
}


def test_no_key_calls_a_write_tool() -> None:
    called = {
        node.func.attr for node in ast.walk(_tree())
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and node.func.attr.startswith("linkedin_")
    }
    assert called == READ_TOOLS, called ^ READ_TOOLS
    from linkedin_server import writes

    assert not called & set(writes.SANCTIONED_WRITES), "a harness key names a sanctioned write"


def test_the_replay_context_is_offline_and_runs_no_script() -> None:
    """STRUCTURAL, because a synthetic document cannot witness it: a capture
    of his settings page carries LinkedIn's own script tags and resource
    addresses, and replaying it must neither run the one nor fetch the other."""
    calls = [node for node in ast.walk(_tree())
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and node.func.attr == "new_context"]
    assert len(calls) == 1
    flags = {kw.arg: kw.value.value for kw in calls[0].keywords if isinstance(kw.value, ast.Constant)}
    assert flags == {"offline": True, "java_script_enabled": False}


def test_every_people_search_asks_for_the_people_and_writes_them_reduced() -> None:
    """THE GO ORDER OF 2026-09-28: the people searches pass include_names=True,
    so each envelope carries people records -- and so each is written REDUCED."""
    calls = [node for node in ast.walk(_tree())
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and node.func.attr == "linkedin_people_search_shape"]
    assert len(calls) == 3
    for call in calls:
        flags = {kw.arg: getattr(kw.value, "value", None) for kw in call.keywords}
        assert flags.get("include_names") is True, ast.unparse(call)
    for key in ("n94", "n84", "n87", "presence", "recruiter", "j107", "n132"):
        assert harness.KEYS[key].get("envelope") == "reduced", key
    assert "N 79" in harness.KEYS["n94"]["rows"]


def test_the_new_readers_cost_one_load_each_and_the_job_search_is_not_one_of_the_five() -> None:
    for key in ("presence", "recruiter", "j107"):
        assert harness.KEYS[key]["loads"] == 1 and not harness.KEYS[key].get("searches"), key
    assert harness.KEYS["j107"]["items"] == ("org",)


def test_a_named_target_is_matched_by_whole_words_and_only_counted() -> None:
    assert harness.name_tokens("  Dara  WHITFIELD, MBA ") == ["dara", "whitfield", "mba"]
    assert harness.person_matches("Dara Whitfield", "dara")
    assert harness.person_matches("Dara Whitfield", "Dara", ["whitfield"])
    assert not harness.person_matches("Dara Whitfield", "dara", ["karlsson"])
    assert not harness.person_matches("Daramir Whitfield", "dara"), "a name inside a longer word"
    assert not harness.person_matches("", "dara") and not harness.person_matches("Dara", "")
    names = harness.names_in({"results": [{"name": "Dara Whitfield"}, {"person": {"name": "Ivo Karlsson"}}],
                              "title": "not a name field"})
    assert sorted(names) == ["Dara Whitfield", "Ivo Karlsson"]
    counts = harness.named_target_counts(names, ["dara", "karlsson", "nobody"])
    assert counts == {"T1": 1, "T2": 1, "T3": 0}
    assert "Dara" not in json.dumps(counts) and "Ivo" not in json.dumps(counts)


def test_the_family_name_is_the_last_word_of_a_multi_word_spelling() -> None:
    key = {"operator": ["Tamsin Stubworth", "tamsin-stubworth-x1", "T Stubworth", "Tamsin", "Tamsin Q"]}
    assert harness.family_names(key) == ["stubworth"]
    assert harness.family_names({}) == []


async def test_p_k1_reads_a_verification_control_by_structure(browser_page) -> None:
    """P K1 (lane S's L.4): a verification badge in the top card, linked to
    the refused settings page, read by structure; its label never returned."""
    await browser_page.set_content(
        "<main><section><h1>" + INVENTED_NAME
        + "<a href='/mypreferences/d/verifications/' aria-label='Verified by " + INVENTED_NAME
        + "'><svg></svg></a></h1><button aria-label='Show verification details' aria-haspopup='dialog'>"
        "</button><span aria-label='Unrelated'></span></section></main>")
    raw = await browser_page.evaluate(harness._VERIFY_JS)
    records = [harness.verify_record(r) for r in raw]
    assert [(r["tag"], r["link"], r["in_heading"], r["haspopup"]) for r in records] == [
        ("a", "mypreferences_verifications", True, "none"),
        ("button", "none", False, "dialog"),
    ]
    assert INVENTED_NAME not in json.dumps(records)
    assert "Verifications" in harness.PROFILE_SECTION_WORDS and "Verifications" in harness.FURNITURE
    assert "verifications" in harness.PATH_WORDS


def test_every_tool_key_reaches_a_tool() -> None:
    body = next(node for node in ast.walk(_tree())
                if isinstance(node, ast.AsyncFunctionDef) and node.name == "_tool")
    source = ast.unparse(body)
    for key, spec in harness.KEYS.items():
        if spec["kind"] == "tool":
            assert "key == '" + key + "'" in source, key
