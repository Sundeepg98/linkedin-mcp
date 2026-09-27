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

Every literal here is invented: the names are the redaction tests' own
invented ones, the slug is ``tests/test_no_committed_identity.py``'s
sanctioned synthetic slug, and every long digit run is built at runtime.
"""
from __future__ import annotations

import ast
import asyncio
import json
import sys
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
    "<label for='s'>Sharing profile edits</label>"
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
                 "\nSharing profile edits\n", 'data-test-hook="UNREAD"', 'data-view-name="settings-toggle"',
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


async def test_one_press_is_read_by_attribute_and_closed_again(browser_page, quick) -> None:
    await browser_page.set_content(_menu_page())
    handle, count = await harness._one_handle(browser_page.locator(harness.MORE_TRIGGER))
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
    handle, _count = await harness._one_handle(browser_page.locator(harness.MORE_TRIGGER))
    with pytest.raises(harness._Anomaly) as stop:
        await harness.press_and_read(browser_page, "in_me_more", handle, False)
    assert stop.value.kind == "the_menu_did_not_close"


async def test_a_conversation_opened_by_a_press_stops_the_session(browser_page, quick) -> None:
    await browser_page.set_content(_menu_page(opens_a_conversation=True))
    handle, _count = await harness._one_handle(browser_page.locator(harness.MORE_TRIGGER))
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
    "<!doctype html><html><body><main><label for='s'>Sharing profile edits</label>"
    "<input id='s' type='checkbox' role='switch'></main>"
    "<script>document.getElementById('s').checked = true;</script></body></html>"
)
ATTRIBUTE_ON = (
    "<!doctype html><html><body><main><label for='s'>Sharing profile edits</label>"
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


def test_every_click_is_the_one_in_press_and_read_and_every_key_press_is_escape() -> None:
    tree = _tree()
    clicks, keys = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "click":
                clicks.append(_enclosing_function(tree, node))
            if node.func.attr == "press":
                keys.append(ast.unparse(node.args[0]) if node.args else "")
    assert clicks == ["press_and_read"], clicks
    assert keys == ["'Escape'"], keys


#: The tools a harness key may call: every one a read.
READ_TOOLS = {
    "linkedin_list_conversations", "linkedin_open_messaging", "linkedin_recent_job_searches",
    "linkedin_premium_job_collection", "linkedin_search_appearances", "linkedin_notifications",
    "linkedin_connections", "linkedin_job_detail", "linkedin_people_search_shape",
    "linkedin_group_memberships", "linkedin_group_page", "linkedin_open_thread",
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


def test_every_tool_key_reaches_a_tool() -> None:
    body = next(node for node in ast.walk(_tree())
                if isinstance(node, ast.AsyncFunctionDef) and node.name == "_tool")
    source = ast.unparse(body)
    for key, spec in harness.KEYS.items():
        if spec["kind"] == "tool":
            assert "key == '" + key + "'" in source, key
