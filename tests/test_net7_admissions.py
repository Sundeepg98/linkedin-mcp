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
