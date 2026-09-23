"""Offline tests for scripts/_probe_l1_admitted_reads_live.py -- no browser.

Everything here exercises the PURE parts of the live harness: argument
selection, digit validation, address building and the pending-REVIEW gate
skip path. Nothing in this file opens a page, a browser or a network
connection -- the module is imported, and only its synchronous, browser-free
functions are called.

The digit-run convention follows the lane's own precedent in
``tests/test_l1_self_scoped_admissions.py``: a five-digit id (``"12345"``)
sits under ``readonly.URN_ID_SHAPE``'s six-digit floor, so it carries no
identifier shape for ``tests/test_no_committed_identity.py`` to see. Longer
digit runs needed for the 20/21-digit boundary are built with the ``*``
repetition operator rather than typed as a long literal, so no 6-or-more
digit run ever appears as contiguous source text.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import _probe_l1_admitted_reads_live as probe  # noqa: E402
from linkedin_server import readonly  # noqa: E402

#: A five-digit id, the lane's own convention -- below URN_ID_SHAPE's
#: six-digit floor, so it is not a real identifier shape.
FIVE = "12345"

# ---------------------------------------------------------------------------
# _selected -- default order
# ---------------------------------------------------------------------------


def test_selected_default_order():
    assert probe._selected([]) == (
        "per_post", "contact", "audience", "overview", "articles", "followers",
    )


def test_selected_default_with_post_id_appends_post_summary():
    assert probe._selected(["--post-id", FIVE]) == (
        "per_post", "contact", "audience", "overview", "articles", "followers",
        "post_summary",
    )


def test_selected_default_with_event_id_appends_event():
    assert probe._selected(["--event-id", FIVE]) == (
        "per_post", "contact", "audience", "overview", "articles", "followers",
        "event",
    )


def test_selected_default_with_both_ids_appends_both_in_order():
    assert probe._selected(["--post-id", FIVE, "--event-id", FIVE]) == (
        "per_post", "contact", "audience", "overview", "articles", "followers",
        "post_summary", "event",
    )


# ---------------------------------------------------------------------------
# _selected -- --only
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", probe.KEYS)
def test_selected_only_a_plain_key(key):
    if key == "post_summary":
        assert probe._selected(["--only", key, "--post-id", FIVE]) == (key,)
    elif key == "event":
        assert probe._selected(["--only", key, "--event-id", FIVE]) == (key,)
    else:
        assert probe._selected(["--only", key]) == (key,)


def test_selected_only_unknown_key_refuses():
    with pytest.raises(SystemExit):
        probe._selected(["--only", "not-a-real-key"])


def test_selected_only_unknown_key_message_lists_the_valid_keys():
    with pytest.raises(SystemExit) as excinfo:
        probe._selected(["--only", "not-a-real-key"])
    message = str(excinfo.value)
    for key in probe.KEYS:
        assert key in message, (key, message)


def test_selected_only_post_summary_without_post_id_refuses():
    with pytest.raises(SystemExit):
        probe._selected(["--only", "post_summary"])


def test_selected_only_event_without_event_id_refuses():
    with pytest.raises(SystemExit):
        probe._selected(["--only", "event"])


# ---------------------------------------------------------------------------
# the digit validator
# ---------------------------------------------------------------------------


def test_digits_accepts_one_digit():
    assert probe._digits_or_none("1") == "1"


def test_digits_accepts_twenty_digits():
    twenty = "1" * probe.MAX_ID_DIGITS
    assert probe._digits_or_none(twenty) == twenty


def test_digits_refuses_zero_digits():
    assert probe._digits_or_none("") is None


def test_digits_refuses_twenty_one_digits():
    assert probe._digits_or_none("1" * (probe.MAX_ID_DIGITS + 1)) is None


def test_digits_refuses_arabic_indic_digits():
    """str.isdigit() is True of these; the ASCII-only charset must not be."""
    arabic_five = "\u0661\u0662\u0663\u0664\u0665"  # Arabic-Indic 1 2 3 4 5
    assert arabic_five.isdigit(), "the fixture itself must exercise the trap"
    assert probe._digits_or_none(arabic_five) is None


def test_digits_refuses_letters():
    assert probe._digits_or_none("abcde") is None


def test_digits_refuses_a_slug_shaped_value():
    assert probe._digits_or_none(FIVE + "-abc") is None


def test_digits_refuses_non_string_input():
    assert probe._digits_or_none(None) is None


# ---------------------------------------------------------------------------
# _validated_id -- the refusal message never echoes the value
# ---------------------------------------------------------------------------


def test_validated_id_accepts_digits():
    assert probe._validated_id(["--post-id", FIVE], "--post-id") == FIVE


def test_validated_id_absent_flag_is_none():
    assert probe._validated_id([], "--post-id") is None


def test_validated_id_refuses_non_digits_without_echoing_the_value():
    planted = "a-value-this-message-must-not-echo"
    with pytest.raises(SystemExit) as excinfo:
        probe._validated_id(["--post-id", planted], "--post-id")
    message = str(excinfo.value)
    assert planted not in message
    assert "not 1-20 ASCII digits" in message


def test_arg_value_dangling_flag_refuses():
    with pytest.raises(SystemExit):
        probe._arg_value(["--post-id"], "--post-id")


# ---------------------------------------------------------------------------
# address builders
# ---------------------------------------------------------------------------


def test_url_for_contact():
    assert probe._url_for("contact", None, None) == probe.CONTACT_URL


def test_url_for_audience():
    assert probe._url_for("audience", None, None) == probe.AUDIENCE_URL


def test_url_for_overview():
    assert probe._url_for("overview", None, None) == probe.OVERVIEW_URL


def test_url_for_articles():
    assert probe._url_for("articles", None, None) == probe.ARTICLES_URL


def test_url_for_followers():
    assert probe._url_for("followers", None, None) == probe.FOLLOWERS_URL


def test_url_for_post_summary_exact_url_for_a_five_digit_id():
    assert probe._url_for("post_summary", FIVE, None) == (
        "https://www.linkedin.com/analytics/post-summary/urn:li:activity:"
        + FIVE + "/"
    )


def test_url_for_event_exact_url_for_a_five_digit_id():
    assert probe._url_for("event", None, FIVE) == (
        "https://www.linkedin.com/events/" + FIVE + "/"
    )


def test_url_for_post_summary_without_an_id_refuses():
    with pytest.raises(ValueError):
        probe._url_for("post_summary", None, None)


def test_url_for_event_without_an_id_refuses():
    with pytest.raises(ValueError):
        probe._url_for("event", None, None)


def test_url_for_per_post_has_no_address():
    """per_post fires no navigation of its own -- _url_for must refuse it."""
    with pytest.raises(ValueError):
        probe._url_for("per_post", None, None)


# ---------------------------------------------------------------------------
# every built address for the five always-admitted keys actually IS admitted
# on this tree
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "key", ["contact", "audience", "overview", "articles", "post_summary"]
)
def test_admitted_addresses_pass_is_read_url(key):
    url = probe._url_for(key, FIVE, None)
    assert readonly.is_read_url(url), (key, url)


@pytest.mark.parametrize(
    "key", ["contact", "audience", "overview", "articles", "post_summary"]
)
def test_admitted_keys_do_not_hit_the_gate_skip(key):
    url = probe._url_for(key, FIVE, None)
    assert probe._gate_check(key, url) is None, key


# ---------------------------------------------------------------------------
# the pending-REVIEW gate skip path, for followers and event
# ---------------------------------------------------------------------------


def test_followers_and_event_hit_the_pending_review_skip_when_the_gate_refuses(
    monkeypatch,
):
    """Monkeypatched rather than read off today's live gate state.

    Both addresses are refused by the shipped gate today (measured:
    ``/follow`` catches followers, no pattern admits an event id), but that
    is a fact about the boundary, not about this script -- a pending REVIEW
    commit could widen it. Forcing ``is_read_url`` False keeps this test
    meaningful regardless of when that commit lands.
    """
    monkeypatch.setattr(probe.readonly, "is_read_url", lambda url: False)
    for key, url in (
        ("followers", probe.FOLLOWERS_URL),
        ("event", probe._url_for("event", None, FIVE)),
    ):
        skip = probe._gate_check(key, url)
        assert skip is not None, key
        assert "REVIEW" in skip, (key, skip)


def test_the_gate_skip_is_none_when_the_gate_admits(monkeypatch):
    """THE OTHER DIRECTION: the skip mechanism itself can turn off."""
    monkeypatch.setattr(probe.readonly, "is_read_url", lambda url: True)
    assert probe._gate_check("followers", probe.FOLLOWERS_URL) is None
