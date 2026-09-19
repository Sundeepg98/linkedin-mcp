"""THE BLAST RADIUS OF THE SEARCH ADMISSION, PINNED BEFORE THE PATTERN LANDS.

`SEARCH-RESULTS-SURFACE` is 20 still-GAP rows, every one a READ, with no
admitted address. The lead ruled admission APPROVED IN PRINCIPLE (`09f9961`,
section 6) under five binding conditions. **This file is conditions 3 and 4,
and it exists BEFORE the pattern by design**:

    3  blast radius measured before the pattern lands, the guard shown
       failing on what it must STILL refuse
    4  the revert path proven BEFORE the admission, not after

**WHY THIS FILE COMES FIRST.** A guard written after an admission is written by
someone who already knows what the pattern matches, and it tends to assert
exactly that. Written first, it is a statement of what the admission MUST NOT
reach, made while nothing is admitted and there is nothing to rationalise.

## THIS FILE DOES NOT ADMIT ANYTHING, AND THAT IS NOT A PARTIAL DELIVERY

Condition 1 requires the admission and a name-free shaper to land in the SAME
commit: *"an implementation that admits the address and defers the shaper has
not partially satisfied this -- it has violated it."* Search results are made
of other people, and an admitted address with no shaper in front of it is the
densest third-party-identity surface on the platform.

So this file lands the guard alone. `MUST_STAY_REFUSED` is the durable half
and stands unchanged after the admission; `ADMISSION_TARGETS` records what the
pattern is *for* and is the only group whose expected value ever changes.

## MEASURED WITH `is_read_url` ON CONCRETE URLS, NEVER A SUBSTRING GREP

This wave produced the case in point earlier the same day: a substring search
over the 32 allowlist patterns reported **32 of 32** "mentioning"
recommendations, which is nonsense. The predicate is the only authority, and a
pattern is only ever exercised through it here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: What the ruling is FOR. Refused today; these are the only entries whose
#: expected value changes when the admission lands WITH its shaper.
ADMISSION_TARGETS = (
    f"{BASE}/search/results/people/?keywords=x",
    f"{BASE}/search/results/all/?keywords=x",
)

#: THE DURABLE HALF. Every one of these must be refused before the admission
#: AND after it. Condition 2 forbids a `/search/` family wildcard, and this is
#: the list that makes that concrete rather than a promise.
MUST_STAY_REFUSED = {
    # Account-ending spellings. The ruling names `close-account` as the risk a
    # family wildcard carries: it is refused today by NO PATTERN MATCHING IT,
    # which is a weaker guarantee than it sounds.
    "close-account": f"{BASE}/psettings/member-account/close-account",
    "close-account-alt": f"{BASE}/settings/close-account",
    "close-account-pref": f"{BASE}/mypreferences/d/close-account",
    # Sibling search verticals a `/search/results/` wildcard would sweep in.
    # Each is its own surface with its own third-party content.
    "search-companies": f"{BASE}/search/results/companies/?keywords=x",
    "search-content": f"{BASE}/search/results/content/?keywords=x",
    "search-groups": f"{BASE}/search/results/groups/?keywords=x",
    "search-schools": f"{BASE}/search/results/schools/?keywords=x",
    "search-events": f"{BASE}/search/results/events/?keywords=x",
    "search-jobs-vertical": f"{BASE}/search/results/jobs/?keywords=x",
    # Third-party identity. The admission is a READ OF A PAGE LISTING PEOPLE
    # and says nothing about reaching any of them individually.
    "third-party-profile": f"{BASE}/in/someone-else/",
    "third-party-contact": f"{BASE}/in/someone-else/detail/contact-info/",
    "third-party-activity": f"{BASE}/in/someone-else/recent-activity/all/",
}


@pytest.mark.parametrize("name", sorted(MUST_STAY_REFUSED))
def test_the_admission_must_never_reach_these(name):
    """THE GUARD. It stands unchanged before and after the pattern lands.

    If one of these ever goes True, the admission was written as a family and
    not as a narrow anchored pattern -- which condition 2 forbids by name.
    """
    url = MUST_STAY_REFUSED[name]
    assert readonly.is_read_url(url) is False, (
        f"{name} became READABLE. The search admission was supposed to be a "
        "narrow anchored pattern; a family wildcard is exactly what condition "
        "2 of the ruling refuses, and this is the surface it was protecting."
    )


def test_the_guard_can_fail_and_is_not_vacuous():
    """SHOWN FAILING. A guard of all-False assertions over a refusing
    predicate would pass just as well on a typo'd URL that matches nothing.

    So the same predicate is exercised on an address KNOWN to be admitted. If
    this ever goes False the predicate has stopped admitting anything and
    every assertion above is passing for the wrong reason.
    """
    assert readonly.is_read_url(f"{BASE}/feed/") is True
    assert readonly.is_read_url(f"{BASE}/in/me/") is True


@pytest.mark.parametrize("url", ADMISSION_TARGETS)
def test_the_targets_are_still_refused_today(url):
    """THE REVERT PATH, condition 4, proven while it is still trivially true.

    This is the assertion that flips when the admission lands. It is pinned
    NOW so the rollback is a known state rather than a reconstruction: revert
    the pattern and this passes again.

    **WHEN THE ADMISSION LANDS WITH ITS SHAPER, THIS TEST IS REWRITTEN AND NOT
    DELETED** -- inverted to assert the targets ARE admitted, so the file
    keeps recording both halves of the transition.
    """
    assert readonly.is_read_url(url) is False


def test_no_search_results_address_is_admitted_yet():
    """The state this whole wave starts from, recorded as a measurement."""
    every = list(ADMISSION_TARGETS) + [
        MUST_STAY_REFUSED[k] for k in MUST_STAY_REFUSED if k.startswith("search-")
    ]
    assert not [u for u in every if readonly.is_read_url(u)]
