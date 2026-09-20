"""THE BLAST RADIUS OF THE SEARCH ADMISSION, PINNED BEFORE THE PATTERN LANDED.

**THE PATTERN LANDED 2026-09-20 AND THIS FILE WAS INVERTED, NOT DELETED**, per
its own instruction below. What landed is the PEOPLE vertical only, with its
shaper and its tool in the same commit. `MUST_STAY_REFUSED` was not touched and
did not go red, which is the measurement that says the admission was narrow --
its six sibling verticals are all still refused. `ADMISSION_TARGETS` split in
two, because one of its two predicted addresses was bought and the other was
not; see the comment on that tuple, which keeps the failed prediction visible
rather than editing it down to the outcome.


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

#: What the ruling is FOR. **INVERTED 2026-09-20 WHEN THE ADMISSION LANDED**,
#: per this file's own instruction -- rewritten, not deleted, so the file keeps
#: recording both halves of the transition.
#:
#: **AND THE TWO ENTRIES DID NOT MOVE TOGETHER, WHICH IS THE FINDING.** This
#: tuple was written on 2026-09-19 as a two-address prediction of what the
#: admission would buy. The admission that landed is the S1 candidate -- the
#: PEOPLE vertical only -- so the first flipped and the second did not. The
#: prediction is kept visible in the split rather than quietly edited down to
#: whatever happened, because a guard rewritten to match the outcome records
#: nothing.
ADMITTED_BY_THE_LANDED_PATTERN = (f"{BASE}/search/results/people/?keywords=x",)

#: **PREDICTED AS A TARGET ON 2026-09-19 AND NOT ADMITTED.** The blended `all`
#: tab serves no row assigned to this blocker -- `N 161` and `M C70` are
#: groups, `N 179` is events, `N 194` is content or the hashtag family, and
#: none of them is `all`. It rides in on no candidate that was measured, so it
#: stayed shut. It sits here rather than in `MUST_STAY_REFUSED` because that
#: set is addresses the admission must NEVER reach, and this is one a later
#: widening could legitimately ask for with its own blast radius.
PREDICTED_BUT_NOT_ADMITTED = (f"{BASE}/search/results/all/?keywords=x",)

#: Both halves, for the assertions that are about the prediction as a whole.
ADMISSION_TARGETS = ADMITTED_BY_THE_LANDED_PATTERN + PREDICTED_BUT_NOT_ADMITTED

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


@pytest.mark.parametrize("url", ADMITTED_BY_THE_LANDED_PATTERN)
def test_the_target_the_pattern_bought_is_admitted(url):
    """THE ASSERTION THAT FLIPPED, condition 4 discharged in the live direction.

    It asserted refusal from 2026-09-19 until the admission landed on
    2026-09-20, and was inverted in that same commit rather than deleted. The
    rollback is therefore a KNOWN state and not a reconstruction: remove the
    one pattern and this assertion returns to its original form.
    """
    assert readonly.is_read_url(url) is True


@pytest.mark.parametrize("url", PREDICTED_BUT_NOT_ADMITTED)
def test_the_target_that_was_predicted_and_not_bought_is_still_refused(url):
    """A PREDICTION THAT DID NOT COME TRUE, kept as an assertion.

    This address was named a target the day before the admission and the
    admission did not buy it. Asserting its refusal is worth more than
    deleting the line: it is now a live guard that the narrow pattern did not
    quietly grow into the blended tab.
    """
    assert readonly.is_read_url(url) is False


def test_exactly_one_search_vertical_is_admitted_and_it_is_people():
    """THE SIZE OF THE ADMISSION, as a measurement rather than a claim.

    The state this wave started from was "no search-results address is
    admitted". That sentence is now false, and replacing it with silence would
    lose the only number that says how far the boundary moved. So it is
    replaced with the COUNT, which goes red in both directions -- if a
    vertical is added without a ruling, and if the people vertical is lost.
    """
    verticals = {
        name: url for name, url in MUST_STAY_REFUSED.items()
        if name.startswith("search-")
    }
    admitted = sorted(n for n, u in verticals.items() if readonly.is_read_url(u))
    assert admitted == [], (
        f"a sibling search vertical is readable: {admitted}. The 2026-09-20 "
        "admission was people-only."
    )
    people = [u for u in ADMITTED_BY_THE_LANDED_PATTERN if readonly.is_read_url(u)]
    assert len(people) == len(ADMITTED_BY_THE_LANDED_PATTERN), (
        "the people vertical is no longer admitted, so the admission was "
        "reverted -- in which case the shaper's tool goes with it, because "
        "condition 1 binds them together in both directions."
    )
