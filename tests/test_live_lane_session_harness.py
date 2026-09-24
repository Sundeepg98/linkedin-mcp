"""The live lane's session harness: the parts that guard the session, offline.

``scripts/_probe_live_lane_session_1.py`` is the ONLY thing standing between
the session and a 41st page load, a load 3 seconds after the last one, and
``/messaging/`` opened while a new message waits. Each of those is a property
of code in that file, so each is asserted here against a fake browser -- no
Chrome, no network, no LinkedIn.

THE THREE THAT MATTER MOST, and each is shown failing in the session
document before the harness was trusted live:

* the ceiling refuses BEFORE the original ``goto`` is called, never after;
* a refused address is never counted as a load;
* ``m43`` / ``m33`` cannot be selected without ``badge`` earlier in the run.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _probe_live_lane_session_1 as harness  # noqa: E402


# --------------------------------------------------------------------------
# Selection -- decided before the browser is touched.
# --------------------------------------------------------------------------


def test_nothing_fires_by_default() -> None:
    with pytest.raises(SystemExit):
        harness._selected([])


def test_an_unknown_key_is_refused() -> None:
    with pytest.raises(SystemExit):
        harness._selected(["--only", "badge,inbox"])


def test_a_key_named_twice_is_refused() -> None:
    with pytest.raises(SystemExit):
        harness._selected(["--only", "badge,badge"])


@pytest.mark.parametrize("key", sorted(harness.MESSAGING_KEYS))
def test_messaging_needs_the_badge_earlier_in_the_same_run(key: str) -> None:
    with pytest.raises(SystemExit):
        harness._selected(["--only", key])
    with pytest.raises(SystemExit):
        harness._selected(["--only", key + ",badge"])
    assert harness._selected(["--only", "badge," + key]) == ["badge", key]


def test_the_order_given_is_the_order_run() -> None:
    assert harness._selected(["--only", "activity,per_post"]) == ["activity", "per_post"]


# --------------------------------------------------------------------------
# The budget and the gap, as pure functions.
# --------------------------------------------------------------------------


def _loads(n: int, last_at: float = 0.0) -> list[dict]:
    return [{"n": i + 1, "at": last_at} for i in range(n)]


def test_the_budget_admits_up_to_the_ceiling_and_not_one_more() -> None:
    assert harness.budget_verdict(_loads(38), 2) is None
    assert harness.budget_verdict(_loads(39), 2) is not None
    assert harness.budget_verdict(_loads(40), 1) is not None


def test_the_gap_is_owed_from_the_last_load() -> None:
    now = 1_000.0
    assert harness.gap_remaining([], now) == 0.0
    assert harness.gap_remaining(_loads(1, now - 5.0), now) == pytest.approx(15.0)
    assert harness.gap_remaining(_loads(1, now - 25.0), now) == 0.0


# --------------------------------------------------------------------------
# The counter wrapped around BROWSER.goto, against a fake.
# --------------------------------------------------------------------------


class _FakeBrowser:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def goto(self, page, url, **kwargs):  # noqa: ANN001 - fake
        from linkedin_server.readonly import assert_read_url

        assert_read_url(url)
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


def test_every_admitted_navigation_is_counted(fake) -> None:
    asyncio.run(harness.BROWSER.goto(None, FEED))
    asyncio.run(harness.BROWSER.goto(None, FEED))
    ledger = json.loads(harness.LEDGER.read_text(encoding="utf-8"))
    assert [row["n"] for row in ledger["loads"]] == [1, 2]
    assert all(row["surface"] == "feed" for row in ledger["loads"])
    assert fake.calls == [FEED, FEED]


def test_the_ceiling_refuses_before_the_navigation(fake) -> None:
    harness.LEDGER.write_text(json.dumps({"loads": _loads(harness.CEILING)}), encoding="utf-8")
    with pytest.raises(harness._LedgerRefusal):
        asyncio.run(harness.BROWSER.goto(None, FEED))
    assert fake.calls == [], "the 41st load reached the browser"
    ledger = json.loads(harness.LEDGER.read_text(encoding="utf-8"))
    assert len(ledger["loads"]) == harness.CEILING


def test_a_refused_address_is_not_a_load(fake) -> None:
    from linkedin_server.readonly import WriteAttemptError

    with pytest.raises(WriteAttemptError):
        asyncio.run(harness.BROWSER.goto(None, "https://www.linkedin.com/my-items/"))
    assert not harness.LEDGER.exists() or not json.loads(
        harness.LEDGER.read_text(encoding="utf-8"))["loads"]


def test_the_gap_is_waited_out_across_processes(tmp_path, monkeypatch) -> None:
    browser = _FakeBrowser()
    monkeypatch.setattr(harness, "BROWSER", browser)
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(harness, "MIN_GAP_S", 0.4)
    harness.LEDGER.write_text(json.dumps({"loads": _loads(1, time.time())}), encoding="utf-8")
    harness._install_counter()
    started = time.monotonic()
    asyncio.run(harness.BROWSER.goto(None, FEED))
    assert time.monotonic() - started >= 0.3


# --------------------------------------------------------------------------
# What leaves the process.
# --------------------------------------------------------------------------


def test_a_string_is_shown_by_length_unless_it_is_a_package_literal() -> None:
    assert harness.shape_of("free text from a page") == "str(len=21)"
    assert harness.shape_of("free text from a page", "text") == "str(len=21)"
    assert harness.shape_of("starred", "active_filter") == "'starred'"
    nested = harness.shape_of({"text": "a sentence", "unread": True, "n": 3})
    assert "a sentence" not in nested and "unread: True" in nested and "n: 3" in nested


def _urn(n: int) -> str:
    # BUILT AT RUNTIME: an urn with six or more digits written out in this file
    # is exactly the shape tests/test_no_committed_identity.py refuses.
    return "urn:li:" + "activity" + ":" + str(n) * 19


def test_a_dict_keyed_by_item_urns_prints_no_key() -> None:
    """THE FIRST LIVE RUN'S LEAK. ``anchors_per_item`` is keyed by item urn."""
    envelope = {"anchors_per_item": {_urn(6): 2, _urn(7): 4}, "pages_loaded": 1}
    rendered = harness.shape_of(envelope)
    assert "urn:li" not in rendered and "666666" not in rendered and "777777" not in rendered
    assert "2 key(s) withheld" in rendered and "pages_loaded: 1" in rendered


def test_an_urn_key_is_withheld_at_every_depth_and_in_list_items() -> None:
    deep = {"a": {"b": {"c": {_urn(8): 1}}}}
    listed = [{_urn(9): 1, "kind": "x"}]
    for value in (deep, listed):
        rendered = harness.shape_of(value)
        assert "urn:li" not in rendered and "888888" not in rendered and "999999" not in rendered


def test_field_names_still_print() -> None:
    assert harness.is_field_name("anchors_per_item")
    assert harness.is_field_name("show_results")
    for bad in (_urn(5), "has space", "x" * 41, "9lives", "id_1234567", ""):
        assert not harness.is_field_name(bad), bad


def test_a_literal_field_still_never_prints_a_long_or_non_ascii_value() -> None:
    assert harness.shape_of("x" * 41, "refused").startswith("str(len=")
    assert harness.shape_of("caf" + chr(0xE9), "refused").startswith("str(len=")


def test_the_surface_is_a_word_never_an_id() -> None:
    assert harness._surface_of("https://www.linkedin.com/feed/update/urn:li:activity:1/") == "feed"
    assert harness._surface_of("https://www.linkedin.com/in/me/") == "in"
    assert harness._surface_of("https://www.linkedin.com/") == "root"


def test_notification_kinds_count_rows_and_print_no_text() -> None:
    rows = [
        {"text": "somebody Invited you to connect", "link": ""},
        {"text": "a stranger followed you", "link": ""},
        {"text": "a card", "link": "https://www.linkedin.com/mynetwork/invitation-manager/"},
        {"text": "your post has 3 reactions", "link": ""},
    ]
    assert harness.notification_kinds(rows) == {
        "invitation_kind_rows": 2, "follow_kind_rows": 1,
    }


def test_urn_types_report_the_type_word_only() -> None:
    # BUILT AT RUNTIME, as _urn below is: a six-digit urn written out here is
    # the shape tests/test_no_committed_identity.py refuses, and this file
    # shipped two of them in its first commit.
    keys = ["urn:li:activity:" + "1" * 6, "urn:li:ugcPost:" + "2" * 6,
            "urn:li:activity:3", "junk"]
    assert harness.urn_types(keys) == {"activity": 2, "ugcPost": 1, "not_an_urn": 1}


def _activity_raw(established, items):
    return {"envelope": {"authorship": {"established": established}, "items": items}}


def test_no_post_id_unless_authorship_is_established() -> None:
    items = [_urn(3)]
    assert harness.newest_own_activity_digits(_activity_raw(False, items)) is None
    assert harness.newest_own_activity_digits(_activity_raw(None, items)) is None
    assert harness.newest_own_activity_digits({}) is None
    assert harness.newest_own_activity_digits(_activity_raw(True, items)) == "3" * 19


def test_the_newest_activity_urn_is_chosen_and_nothing_else_counts() -> None:
    other = "urn:li:" + "ugcPost" + ":" + "9" * 19
    items = [_urn(2), other, _urn(4), "junk", "urn:li:activity:" + "1" * 21,
             "urn:li:activity:12a4"]
    assert harness.newest_own_activity_digits(_activity_raw(True, items)) == "4" * 19


def test_a_notify_toggle_is_counted_and_its_label_never_returned() -> None:
    fields = [
        {"label": "First name", "role": "textbox"},
        {"label": "Share profile updates with your network", "role": "switch",
         "type": "checkbox", "checked": False},
        {"name": "Notify network", "role": "checkbox"},
        "not a dict",
    ]
    found = harness.notify_controls(fields)
    assert found["fields"] == 4 and found["notify_like_controls"] == 2
    rendered = harness.shape_of(found)
    assert "Share profile" not in rendered and "Notify" not in rendered
    assert found["matches"][0] == {"role": "switch", "type": "checkbox", "carries_checked": True}
    assert harness.notify_controls([{"label": "City"}])["notify_like_controls"] == 0


def test_the_capture_keys_are_constant_addresses_the_boundary_admits() -> None:
    from linkedin_server import readonly

    for key, url in harness.CAPTURE_URLS.items():
        assert readonly.is_read_url(url), key
        assert "{" not in url and "?" not in url, key
    assert set(harness.CAPTURE_URLS) <= set(harness.KEYS)
    assert set(harness.L1_KEYS) <= set(harness.KEYS)


def test_the_environment_refuses_without_attach_mode(monkeypatch) -> None:
    monkeypatch.setattr(harness.config, "CDP_ATTACH", False)
    assert harness._environment_refusal() is not None
    monkeypatch.setattr(harness.config, "CDP_ATTACH", True)
    monkeypatch.setattr(harness.config, "MIN_NAVIGATION_INTERVAL_S", 3.0)
    assert harness._environment_refusal() is not None
    monkeypatch.setattr(harness.config, "MIN_NAVIGATION_INTERVAL_S", 20.0)
    assert harness._environment_refusal() is None
