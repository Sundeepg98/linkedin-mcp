"""THE BLAST RADIUS OF THE SEARCH ADMISSION, PINNED BEFORE THE PATTERN LANDED.

**WIDENED 2026-09-24, AND INVERTED A SECOND TIME RATHER THAN EDITED DOWN.**
`D2-SEARCH-VERTICALS-WIDENED` (the orchestrator's delegated call) widened the
people line to four closed words, `(people|companies|groups|events)`, and
`MUST-STAY-REFUSED-ENTRIES-COME-OUT` (2026-09-19) had already said what that
does to this file: the vertical entries in `MUST_STAY_REFUSED` assumed S1, so
they "come out, or move to a clearly-marked conditional block naming [the
choice] they assume", while "the account-ending and third-party families stay
-- those are durable under every candidate." So `companies`, `groups` and
`events` left `MUST_STAY_REFUSED` for `ADMITTED_BY_THE_D2_WIDENING`, which
asserts them ADMITTED; `content`, `schools` and `jobs` moved to
`REFUSED_UNDER_THE_D2_CHOICE`, marked with the choice they assume; and the
durable set GAINED the account-ending traversal from each of the four words,
which is durable under every closed spelling. The count test below was
rewritten, not relaxed: it now pins FOUR and still goes red both ways, and a
planted `/search/` prefix is shown turning it.

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

import re
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

#: THE THREE THE 2026-09-24 WIDENING BOUGHT. **UNTIL THAT DAY EACH OF THESE
#: SAT IN `MUST_STAY_REFUSED` BELOW**, under these same names, asserting the
#: opposite. They moved on `MUST-STAY-REFUSED-ENTRIES-COME-OUT` -- entries that
#: assumed S1 come out when the choice changes -- and they are kept here,
#: asserted the other way, so the transition stays on the record rather than
#: vanishing from it.
ADMITTED_BY_THE_D2_WIDENING = {
    "search-companies": f"{BASE}/search/results/companies/?keywords=x",
    "search-groups": f"{BASE}/search/results/groups/?keywords=x",
    "search-events": f"{BASE}/search/results/events/?keywords=x",
}

#: THE CONDITIONAL BLOCK THE RULING ASKED FOR. **THESE ARE REFUSED BECAUSE OF
#: A CHOICE, AND THE CHOICE IS D2's**: four closed words, not seven. Each is
#: its own surface with its own third-party content, and a later widening may
#: legitimately ask for one with its own blast radius -- which is exactly why
#: they are not in the durable set below. `content` is the one a census row
#: names (`M C70`'s own address in the address table, and `N 194`'s candidate
#: route); `D2-SEARCH-VERTICALS-WIDENED` did not reach it.
REFUSED_UNDER_THE_D2_CHOICE = {
    "search-content": f"{BASE}/search/results/content/?keywords=x",
    "search-schools": f"{BASE}/search/results/schools/?keywords=x",
    "search-jobs-vertical": f"{BASE}/search/results/jobs/?keywords=x",
}

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
    # THE ACCOUNT-ENDING TRAVERSAL, FROM EACH OF THE FOUR WORDS. Added
    # 2026-09-24. The people spelling is the one the 2026-09-19 preconditions
    # measured ADMITTED under both wildcards and named by no forbidden
    # substring; a closed word cannot be followed by `..`, and that holds for
    # the three new words exactly as it held for the first.
    "traversal-people": (
        f"{BASE}/search/results/people/../../mypreferences/d/close-account"),
    "traversal-companies": (
        f"{BASE}/search/results/companies/../../mypreferences/d/close-account"),
    "traversal-groups": (
        f"{BASE}/search/results/groups/../../mypreferences/d/close-account"),
    "traversal-events": (
        f"{BASE}/search/results/events/../../mypreferences/d/close-account"),
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


@pytest.mark.parametrize("name", sorted(ADMITTED_BY_THE_D2_WIDENING))
def test_the_three_the_widening_bought_are_admitted(name):
    """INVERTED 2026-09-24 FROM `test_the_admission_must_never_reach_these`.

    Each of these asserted refusal there, under its same name, until the
    widening landed. The rollback is the people-only line, which returns every
    one of them to that assertion.
    """
    assert readonly.is_read_url(ADMITTED_BY_THE_D2_WIDENING[name]) is True


@pytest.mark.parametrize("name", sorted(REFUSED_UNDER_THE_D2_CHOICE))
def test_the_verticals_the_d2_choice_leaves_out_are_refused(name):
    """Refused because D2 chose four words, and marked as a choice.

    If one of these ever goes True, the widening grew past what was ruled --
    or a new ruling reached it, in which case it moves out of this block the
    way the three above moved out of the durable one.
    """
    assert readonly.is_read_url(REFUSED_UNDER_THE_D2_CHOICE[name]) is False


#: EVERY VERTICAL WORD THIS REPOSITORY HAS WRITTEN DOWN, recorded or plausible
#: (`scripts/_probe_search_admission_blast_radius.py`'s corpus, plus
#: `newsletters` from `search_results.RESULT_TABLE`). The count below is taken
#: over this closed list, so a vertical nobody named is invisible to it; the
#: planted spellings a closed word must refuse are driven in
#: `tests/test_d2_search_verticals.py`.
KNOWN_VERTICALS = (
    "all", "companies", "content", "courses", "events", "groups", "jobs",
    "newsletters", "people", "products", "schools", "services",
)


def _admitted_verticals() -> list[str]:
    return sorted(
        word for word in KNOWN_VERTICALS
        if readonly.is_read_url(f"{BASE}/search/results/{word}/?keywords=x")
    )


def test_exactly_the_four_d2_verticals_are_admitted():
    """THE SIZE OF THE ADMISSION, as a measurement rather than a claim.

    REWRITTEN 2026-09-24 FROM `test_exactly_one_search_vertical_is_admitted_
    and_it_is_people`, which pinned ONE, and before that the state was "no
    search-results address is admitted". The number is what says how far the
    boundary moved each time, so it is replaced rather than dropped. It goes
    red in both directions -- a vertical added without a ruling, and any of
    the four lost.
    """
    admitted = _admitted_verticals()
    assert admitted == ["companies", "events", "groups", "people"], (
        f"the admitted search verticals are {admitted}. D2-SEARCH-VERTICALS-"
        "WIDENED admitted exactly people, companies, groups and events."
    )
    people = [u for u in ADMITTED_BY_THE_LANDED_PATTERN if readonly.is_read_url(u)]
    assert len(people) == len(ADMITTED_BY_THE_LANDED_PATTERN), (
        "the people vertical is no longer admitted, so the admission was "
        "reverted -- in which case the shaper's tool goes with it, because "
        "condition 1 binds them together in both directions."
    )


def test_a_planted_search_prefix_turns_the_count_and_the_durable_set_red():
    """SHOWN FAILING: the count and the durable set over a boundary with a
    `/search/` PREFIX planted in it -- condition 2's named trap. Every one of
    the twelve words must go True under it, and so must the account-ending
    traversal, or neither assertion above is measuring what it claims to."""
    original = readonly._ALLOWED_URL_PATTERNS
    readonly._ALLOWED_URL_PATTERNS = original + (
        re.compile(r"^https://www\.linkedin\.com/search/"),
    )
    try:
        admitted = _admitted_verticals()
        traversals = [
            name for name, url in MUST_STAY_REFUSED.items()
            if name.startswith("traversal-") and readonly.is_read_url(url)
        ]
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    assert admitted == sorted(KNOWN_VERTICALS)
    assert len(traversals) == 4, (
        f"the planted prefix admitted {len(traversals)} of the four traversal "
        "spellings; it should admit all four, so the durable set is not "
        "seeing the trap it names"
    )
    # And the boundary is itself again.
    assert _admitted_verticals() == ["companies", "events", "groups", "people"]
