"""Lane net7's admissions (2026-11-27), each one anchored line on the orchestrator's ruling, its census lines in the same commit.

* ``/mynetwork/discovery-see-all/`` -- his full People You May Know lists
  (census ``N 97``, ``N 98``, ``N 62``), on GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL:
  the Grow tab's first render draws no suggestion module (live session 12,
  load 8) and SCROLL-NOT-SANCTIONED stands, so the lists are read at their own
  address. Refused by allowlist silence alone, so it is READ-PAST-AN-ACT-
  SUBSTRING's second clause: one anchored line, no query, no sub-path, no
  exemption.

Each admission is held two ways: the address admitted, and every NEAR MISS --
a query, a sub-path, a sibling page, a longer word, a traversal -- still
refused, which is the control that shows the line is anchored.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import readonly
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = Path(__file__).resolve().parents[1]
B = "https://www.linkedin.com"

DISCOVERY = f"{B}/mynetwork/discovery-see-all/"


@pytest.mark.parametrize("address", [DISCOVERY, DISCOVERY.rstrip("/")])
def test_his_full_suggestion_lists_are_admitted(address) -> None:
    assert readonly.is_read_url(address) is True


@pytest.mark.parametrize("address, why", [
    (DISCOVERY + "?x=1", "a query -- where a filter naming a person would arrive"),
    (DISCOVERY + "people/", "a sub-path"),
    (f"{B}/mynetwork/discovery-see-allx/", "a longer word"),
    (f"{B}/mynetwork/discover-hub/", "the Discover-more hub: drawn, not admitted here"),
    (f"{B}/mynetwork/grow/", "the Grow tab /mynetwork/ lands on: not admitted here"),
    (f"{B}/mynetwork/import-contacts/", "the address-book import page"),
    (f"{B}/mynetwork/discovery-see-all/../../in/someone-else/", "a traversal onto a third party"),
    ("http://www.linkedin.com/mynetwork/discovery-see-all/", "not https"),
])
def test_every_near_miss_of_the_suggestion_lists_stays_refused(address, why) -> None:
    assert readonly.is_read_url(address) is False, why


def test_the_suggestion_lists_need_no_exemption() -> None:
    """Allowlist silence alone refused it: no forbidden substring is in it,
    and no pattern exemption names it."""
    lowered = DISCOVERY.lower()
    assert [bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in lowered] == []
    for pattern, _excused in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS:
        assert not pattern.match(DISCOVERY), pattern.pattern


def test_the_line_is_one_anchored_pattern() -> None:
    lines = [p.pattern for p in readonly._ALLOWED_URL_PATTERNS if "discovery-see-all" in p.pattern]
    assert lines == [r"^https://www\.linkedin\.com/mynetwork/discovery-see-all/?$"]
    source = (REPO / "linkedin_server" / "readonly.py").read_text(encoding="utf-8")
    assert source.count("discovery-see-all/?$") == 1
    assert "GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL" in source


# ---------------------------------------------------------------------------
# The received tab's own leaf (census N 13), in this lane on the orchestrator's
# ruling of 2026-11-27 13:25: "one reader must not be split across two lanes".
# Live session 12 loaded /mynetwork/invitation-manager/ and LinkedIn landed it
# one level deeper (load 28); readers-net26's landed_elsewhere refusal of that
# landing is the red case.
# ---------------------------------------------------------------------------

RECEIVED_LEAF = f"{B}/mynetwork/invitation-manager/received/"
WORDS_12 = REPO / "tests" / "fixtures" / "synthetic" / "live12_invitation_pills_words.html"


@pytest.mark.parametrize("address", [RECEIVED_LEAF, RECEIVED_LEAF.rstrip("/")])
def test_the_received_leaf_is_admitted(address) -> None:
    assert readonly.is_read_url(address) is True


@pytest.mark.parametrize("address, why", [
    (RECEIVED_LEAF + "?filterCriteria=x", "a query -- a filter's own line, if ever"),
    (RECEIVED_LEAF + "x/", "a sub-path"),
    (f"{B}/mynetwork/invitation-manager/receivedx/", "a longer word"),
    (f"{B}/mynetwork/invitation-manager/sent/withdraw/", "a withdraw"),
    (f"{B}/mynetwork/invite-connect/invitations/", "the other invitation surface"),
    ("http://www.linkedin.com/mynetwork/invitation-manager/received/", "not https"),
])
def test_every_near_miss_of_the_received_leaf_stays_refused(address, why) -> None:
    assert readonly.is_read_url(address) is False, why


def test_the_received_leaf_excuses_exactly_invitation() -> None:
    """It trips one forbidden substring, measured, and its one exemption
    excuses exactly that for exactly this address: the tuple is unchanged."""
    lowered = RECEIVED_LEAF.lower()
    assert [bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in lowered] == ["invitation"]
    excused = [ex for pattern, ex in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
               if pattern.match(RECEIVED_LEAF)]
    assert excused == [frozenset({"invitation"})]


def test_the_received_reader_accepts_the_leaf_it_lands_on() -> None:
    from linkedin_server import invitation_manager as im

    assert im.landed_on_received(RECEIVED_LEAF) is True
    assert im.landed_on_received(RECEIVED_LEAF.rstrip("/")) is True
    assert im.landed_on_received(im.RECEIVED_URL) is True
    assert im.landed_on_received(im.SENT_URL) is False
    assert im.landed_on_received(RECEIVED_LEAF + "x/") is False


async def test_the_received_reader_reads_session_12s_capture(browser_page) -> None:
    """The page at the leaf reads as session 11's did: two invitations to
    connect and a Page's newsletter invitation, LinkedIn's words put back
    by keyed shape (``scripts/_build_live12_net7_word_skeletons.py``)."""
    from linkedin_server import invitation_manager as im

    async def _refused(route) -> None:  # noqa: ANN001 - a playwright route
        await route.abort()

    await browser_page.route("**/*", _refused)
    await browser_page.set_content(WORDS_12.read_text(encoding="ascii"), wait_until="domcontentloaded")
    out = await im.read_received_invitations(browser_page)
    assert (out["side"], out["refused"]) == ("received", None)
    assert (out["rows_seen"], out["rows_read"]) == (3, 3)
    assert out["kinds"] == {"connection": 2, "newsletter": 1, "other": 0}
