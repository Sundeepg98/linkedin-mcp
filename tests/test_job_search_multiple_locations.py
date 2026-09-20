"""The multi-location fan-out, and the two url spellings it must never build.

Census row ``J 151`` -- filter a job search by MULTIPLE simultaneous locations
-- sat GAP with a MEASURED reason rather than an unmeasured one. On 2026-09-05
both plausible url spellings were fired live, with city A alone returning seven
postings and city B alone seven, sharing two:

    location=A%2C%20B       KEPT by LinkedIn. Seven postings, of which ZERO
                            are A-only and ZERO are B-only -- the comma-joined
                            string geocodes somewhere neither search reaches.
    location=A&location=B   STRIPPED. LinkedIn serves the LAST city alone
                            (0 of A-only, 5 of B-only).

So the capability is SEVERAL LOADS, not a second spelling of one url, and that
is what shipped: ``locations``, semicolon-separated, one page load per place,
merged and de-duplicated.

=============================================================================
WHAT EACH GUARD BELOW IS FOR, AND THE CONTROL THAT MAKES IT READABLE
=============================================================================

**1. The url guard is the one that matters.** A fan-out is a new writer of
search urls, and the two measured-wrong spellings are exactly what a careless
fan-out would produce -- join the places with a comma, or append ``location``
twice. ``_wrong_location_spellings`` is the predicate, and it is run over BOTH
the live tool's navigations and over ``_MEASURED_WRONG_URLS``, the two literal
urls measured wrong on 2026-09-05, kept here permanently. A check that has only
ever been seen passing certifies nothing; this one is shown catching the exact
pair it exists for, every run.

**2. Every refusal has a control that is ACCEPTED.** ``locations_plan`` refuses
four ways -- both arguments at once, no place names, one place name, too many.
A refusal test on its own cannot tell "refuses the bad input" from "refuses
everything", so each is paired with the nearest input that must go through.

**3. The comma trap is the reason the separator is a semicolon**, and it gets
its own pair: a qualified place carrying two commas of its own parses as ONE
place, while two cities a caller comma-separated is refused rather than handed
to LinkedIn as the string measured to geocode elsewhere.

=============================================================================
PLACE NAMES HERE ARE INVENTED, AND THAT IS NOT DECORATION
=============================================================================

This repository does not put a real city in a tracked file. The names below
follow the ones ``tests/test_tools.py``'s own card fixtures already use, so a
reader can tell at a glance that nothing here is a location anybody lives in.
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qs, urlsplit

import pytest

from linkedin_server import jobfilter
from linkedin_server.server import linkedin_search_jobs

from tests.conftest import FakePage
from tests.test_tools import (  # noqa: F401 - drive is used by injection
    SEARCH_CARD,
    drive,
)

# ---------------------------------------------------------------------------
# Invented places. Three of them, because two can be told apart by accident --
# a bug that returned "the first" and a bug that returned "the last" look
# identical on a pair, and only differ when there is a middle.
# ---------------------------------------------------------------------------

#: EVERY PROPER NOUN HERE IS ALREADY IN THE TRACKED TREE -- "Riverton",
#: "Fairhaven", "Ashgrove" and "Northgate" are this repository's own invented
#: vocabulary, used 86, 82, 56 and 10 times respectively before this file
#: existed. Coining a NEW placename would have been the riskier move: a
#: plausible-sounding invention is one search away from being somewhere real,
#: and the identity wordlist that would otherwise catch it is gitignored, so it
#: runs DISARMED in a worktree like this one. Recombining tokens the repo has
#: already vetted adds no new proper noun at all.
PLACE_A = "Riverton, Fairhaven, United States"
PLACE_B = "Ashgrove, Fairhaven, United States"
PLACE_C = "Northgate, Fairhaven, United States"

SEP = jobfilter.LOCATIONS_SEPARATOR


def _cards(*job_ids: str) -> list[dict[str, Any]]:
    """Copies of the shared search card differing only in their job id."""

    return [
        {**SEARCH_CARD, "href": SEARCH_CARD["href"].replace("4111222333", job_id)}
        for job_id in job_ids
    ]


class PagePerLoad(FakePage):
    """A FakePage that answers each navigation with its OWN set of cards.

    The shared ``FakePage`` hands back one ``evaluate_result`` forever, which
    is right for a one-load tool and useless for a fan-out: every place would
    return the identical postings, the de-duplicator would eat all but the
    first, and a merge that dropped whole places would look exactly like a
    merge that worked.

    SUBCLASSED RATHER THAN RE-IMPLEMENTED, because ``tests/conftest.py``'s own
    header records what a narrower stand-in costs: a fake that models a smaller
    signature than the real API fails where the real one succeeds, and a broad
    ``except`` upstream turns that into a plausible answer. Everything except
    the per-load swap is inherited unchanged.
    """

    def __init__(self, per_load: list[list[dict[str, Any]]], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._per_load = list(per_load)
        self._loads = 0
        self.evaluate_result = self._per_load[0] if self._per_load else []

    async def goto(self, url: str, **kwargs: Any) -> None:
        # THE CURSOR ADVANCES ON THE WAY IN, NOT ON THE WAY OUT, and the first
        # draft of this fake got it backwards. Incrementing AFTER the goto
        # served the SECOND set of cards to the FIRST harvest, so both loads
        # saw the same postings, the de-duplicator ate one place entirely, and
        # the result -- two rows out of a merge that should have produced
        # three -- was a perfectly plausible number. Caught by the end-to-end
        # test below, which is the reason it exists alongside the unit tests
        # for the merge: a correct merge called with the wrong rows returns a
        # correct-looking answer.
        await super().goto(url, **kwargs)
        index = min(self._loads, len(self._per_load) - 1)
        self._loads += 1
        self.evaluate_result = self._per_load[index] if self._per_load else []


# ---------------------------------------------------------------------------
# 1. THE URL GUARD, and the known-bad pair it is shown catching.
# ---------------------------------------------------------------------------

#: The two spellings fired live on 2026-09-05 and found WRONG. Kept as literal
#: urls so the predicate below is exercised against the real thing rather than
#: against a description of it.
_MEASURED_WRONG_URLS = (
    "https://www.linkedin.com/jobs/search/?keywords=node.js+engineer"
    "&location=Riverton%2C+Fairhaven%2C+United+States%2C+Ashgrove%2C"
    "+Fairhaven%2C+United+States",
    "https://www.linkedin.com/jobs/search/?keywords=node.js+engineer"
    "&location=Riverton%2C+Fairhaven%2C+United+States"
    "&location=Ashgrove%2C+Fairhaven%2C+United+States",
)


def _wrong_location_spellings(urls: list[str], places: list[str]) -> list[str]:
    """Every url that spells more than one place into a single request.

    Two shapes, one per measured failure:

    * the ``location`` key appearing MORE THAN ONCE in one url -- the spelling
      LinkedIn strips down to the last city;
    * a single ``location`` value carrying more than one of the requested
      places -- the comma-joined spelling LinkedIn keeps and geocodes
      elsewhere.

    The second is matched on the PLACES THIS CALL ASKED FOR rather than on a
    comma, because a comma inside one qualified place is legitimate and common:
    a predicate that flagged any comma would refuse every real LinkedIn place
    name and would be noise rather than a guard.
    """

    guilty: list[str] = []
    for url in urls:
        values = parse_qs(urlsplit(url).query, keep_blank_values=True).get(
            "location", []
        )
        if len(values) > 1:
            guilty.append(url)
            continue
        for value in values:
            if sum(1 for place in places if place and place in value) > 1:
                guilty.append(url)
                break
    return guilty


def test_the_url_guard_catches_both_spellings_measured_wrong():
    """THE CONTROL, and it runs first because nothing below means anything
    without it.

    The identical predicate the live test uses, aimed at the two literal urls
    measured wrong on 2026-09-05. If this goes green-by-vacuity -- a predicate
    that returns nothing for any input -- the guard beside it would pass on a
    tool that built either of them.
    """
    caught = _wrong_location_spellings(
        list(_MEASURED_WRONG_URLS), [PLACE_A, PLACE_B]
    )
    assert len(caught) == 2, (
        "the url predicate let a measured-wrong spelling through: caught "
        f"{len(caught)} of 2 -- {caught}"
    )


async def test_a_fan_out_builds_one_url_per_place_and_never_joins_them(drive):
    """Three places, three navigations, and not one multi-place url.

    This is the whole safety argument of the feature in one assertion: the
    capability is reached by loading more pages, never by inventing a url
    shape LinkedIn was measured to mishandle.
    """
    page = PagePerLoad(
        [_cards("4111222301"), _cards("4111222302"), _cards("4111222303")]
    )
    navigations = drive(page)

    result = await linkedin_search_jobs(
        keywords="node.js engineer",
        locations=f"{PLACE_A}{SEP} {PLACE_B}{SEP} {PLACE_C}",
    )

    assert "error" not in result, result
    assert len(navigations) == 3, navigations
    assert result["pages_loaded"] == 3, result

    guilty = _wrong_location_spellings(navigations, [PLACE_A, PLACE_B, PLACE_C])
    assert not guilty, (
        "a fan-out url spelled more than one place into a single request -- "
        "both such spellings were measured wrong on 2026-09-05, one geocoding "
        f"to neither city and one stripped to the last: {guilty}"
    )

    for place, url in zip((PLACE_A, PLACE_B, PLACE_C), navigations):
        values = parse_qs(urlsplit(url).query).get("location", [])
        assert values == [place], (url, values)


async def test_one_location_builds_exactly_the_url_it_always_built(drive):
    """The single-place path is untouched by the fan-out landing beside it.

    ``locations`` re-plumbed how the location reaches the url -- it is now
    spliced per search rather than appended once -- so the ordinary call is
    the regression risk, not the new one. Keywords first, location second,
    one navigation.
    """
    page = FakePage(evaluate_result=_cards("4111222311"))
    navigations = drive(page)

    result = await linkedin_search_jobs(
        keywords="node.js engineer", location=PLACE_A, job_type="full_time"
    )

    assert "error" not in result, result
    assert len(navigations) == 1, navigations
    assert result["pages_loaded"] == 1, result
    assert result["query"]["locations"] is None, result["query"]
    query = urlsplit(navigations[0]).query
    assert query.startswith("keywords="), query
    assert parse_qs(query)["location"] == [PLACE_A], query
    assert parse_qs(query)["f_JT"] == ["F"], query


async def test_a_refused_plan_loads_no_page_at_all(drive):
    """A refusal costs zero navigations, which is why the plan runs first.

    A fan-out that validated its arguments after the first load would have
    already put a search in the operator's own recent-search history before
    deciding it could not honour the call.
    """
    page = FakePage(evaluate_result=_cards("4111222321"))
    navigations = drive(page)

    result = await linkedin_search_jobs(
        keywords="node.js engineer", location=PLACE_A, locations=f"{PLACE_B}{SEP}{PLACE_C}"
    )

    assert result["error"] == "bad_argument", result
    assert navigations == [], navigations


# ---------------------------------------------------------------------------
# 2. THE PLAN. Every refusal paired with the nearest input that is accepted.
# ---------------------------------------------------------------------------


def test_no_locations_is_the_ordinary_single_search():
    plan = jobfilter.locations_plan(PLACE_A, "")
    assert plan["state"] == "single", plan
    assert plan["places"] == [PLACE_A], plan


def test_an_empty_location_is_still_a_single_search():
    """LinkedIn's default is a real answer and must not be refused."""
    plan = jobfilter.locations_plan("", "")
    assert plan["state"] == "single", plan
    assert plan["places"] == [""], plan


def test_two_places_are_a_fan_out():
    """THE CONTROL FOR EVERY REFUSAL BELOW. Without it, a plan that refused
    every input would pass all four of them."""
    plan = jobfilter.locations_plan("", f"{PLACE_A}{SEP} {PLACE_B}")
    assert plan["state"] == "fanout", plan
    assert plan["places"] == [PLACE_A, PLACE_B], plan


def test_both_arguments_together_are_refused():
    plan = jobfilter.locations_plan(PLACE_A, f"{PLACE_B}{SEP}{PLACE_C}")
    assert plan["state"] == "refused", plan
    assert plan["places"] == [], plan
    assert "both" in plan["why"].lower(), plan["why"]


def test_separators_without_place_names_are_refused():
    plan = jobfilter.locations_plan("", f" {SEP} {SEP} ")
    assert plan["state"] == "refused", plan
    assert "no place names" in plan["why"], plan["why"]


def test_one_place_in_the_plural_argument_is_refused():
    """The comma trap, refused rather than guessed at.

    One entry is either a caller who wanted ``location``, or a caller who
    comma-separated two cities -- and that second reading is the 2026-09-05
    failure, where LinkedIn keeps the joined string and returns postings from
    neither city. Both readings are cleared by the same one-line fix, so the
    refusal costs the caller nothing.
    """
    plan = jobfilter.locations_plan("", f"Riverton, Calderbrook{SEP}")
    assert plan["state"] == "refused", plan
    assert "ONE place" in plan["why"], plan["why"]
    # The diagnostic a caller acts on: how many commas were sitting in there.
    assert "1 comma(s)" in plan["why"], plan["why"]


def test_the_refusal_never_quotes_the_place_the_caller_typed():
    """Counts and shapes, never the value. The rule this module states.

    Aimed at the refusal most likely to carry its input -- the one that
    describes a single ambiguous entry -- with a needle distinctive enough
    that a substring test cannot pass by coincidence.
    """
    # A NEEDLE THAT IS NOT A NAME OF ANYTHING. It has to be distinctive enough
    # that a substring test cannot pass by coincidence AND not be a place, a
    # person or an employer -- so it is letters repeated, not an invention that
    # might turn out to be somewhere real.
    needle = "Aaaaaaaa"
    plan = jobfilter.locations_plan("", f"{needle}, Bbbbbbbb{SEP}")
    assert plan["state"] == "refused", plan
    assert needle not in plan["why"], plan["why"]
    assert "Bbbbbbbb" not in plan["why"], plan["why"]


def test_a_qualified_place_keeps_its_own_commas():
    """Two commas inside one place is ONE place, not three.

    This is why the separator is a semicolon. Splitting on commas would turn
    a single LinkedIn-spelled place into three searches for things that are
    not places, and nothing would say so.
    """
    assert jobfilter.split_locations(PLACE_A) == [PLACE_A]
    assert jobfilter.split_locations(f"{PLACE_A}{SEP}{PLACE_B}") == [
        PLACE_A,
        PLACE_B,
    ]


def test_duplicate_places_collapse_instead_of_costing_a_load():
    plan = jobfilter.locations_plan(
        "", f"{PLACE_A}{SEP} {PLACE_A.upper()} {SEP}{PLACE_B}"
    )
    assert plan["state"] == "fanout", plan
    assert plan["places"] == [PLACE_A, PLACE_B], plan
    assert "1 duplicate(s) collapsed" in plan["why"], plan["why"]


def test_the_ceiling_refuses_one_more_than_it_accepts():
    """The cap shown accepting its maximum and refusing the next one.

    THE FIRST DRAFT OF THIS TEST COULD NOT FAIL, and a mutation run is what
    said so. It built both inputs out of ``jobfilter.MAX_LOCATIONS``, so
    raising the constant to 500 raised the test's own inputs with it and the
    assertion stayed green against a cap that refused nothing. A check whose
    input is derived from the value under test measures the derivation, never
    the value.

    So the number is pinned as a LITERAL here. That makes re-costing the budget
    fail in this file, which is the intent and not a nuisance: ``MAX_LOCATIONS``
    is a declared cost budget on this server rather than a measured LinkedIn
    limit, and moving it should cost somebody a deliberate edit and a reason.
    """
    assert jobfilter.MAX_LOCATIONS == 5, (
        "the location budget moved. It is a POLICY number -- one page load per "
        "place, each a row in the operator's own recent-search history -- not "
        "a measured LinkedIn limit. Change it here and in jobfilter.py "
        "together, and say in the commit why the cost changed."
    )
    at_the_cap = SEP.join(f"City {n}, Region, Country" for n in range(5))
    over = SEP.join(f"City {n}, Region, Country" for n in range(6))
    assert jobfilter.locations_plan("", at_the_cap)["state"] == "fanout"
    refused = jobfilter.locations_plan("", over)
    assert refused["state"] == "refused", refused
    assert "5" in refused["why"], refused["why"]
    assert "budget" in refused["why"], refused["why"]


def test_the_cap_is_declared_a_budget_and_not_a_measurement():
    """The number is a policy choice and the source has to say so.

    This repository's standing rule is that a stated number carries its
    evidence. ``MAX_LOCATIONS`` was NOT measured against LinkedIn, and a
    future reader must not be able to mistake it for a reading.
    """
    doc = jobfilter.__doc__ or ""
    source = jobfilter.locations_plan.__doc__ or ""
    assert doc or source
    import inspect

    text = inspect.getsource(jobfilter)
    window = text.split("MAX_LOCATIONS = ")[0][-900:]
    assert "BUDGET AND NOT A MEASUREMENT" in window.upper(), window[-300:]


# ---------------------------------------------------------------------------
# 3. THE MERGE. Round-robin, de-duplicated, and each place accounted for.
# ---------------------------------------------------------------------------


def _envelope(place_rows: list[str], *, page_had: Optional[int] = None) -> dict[str, Any]:
    """An envelope shaped the way ``shape.envelope`` shapes one."""

    rows = [
        {"title": "Senior Node.js Developer", "job_id": job_id, "location": "Remote"}
        for job_id in place_rows
    ]
    return {
        "count": len(rows),
        "page_had": len(rows) if page_had is None else page_had,
        "capped": False,
        "limit": 25,
        "pages_loaded": 1,
        "source_url": "https://www.linkedin.com/jobs/search/?keywords=x",
        "results": rows,
    }


def test_the_merge_is_round_robin_so_a_trim_falls_evenly():
    """THE DEFECT THIS ORDERING EXISTS FOR, pinned as a behaviour.

    Concatenation is the obvious merge and it is silently wrong at this tool's
    measured numbers: three places at the measured window of seven is 21 rows
    against a default limit of 25, five places is 35, and a concatenated list
    trimmed to the limit drops the LAST places entirely. The caller sees
    ``capped`` true and nothing saying which place vanished.
    """
    merged = jobfilter.merge_location_reads(
        [
            (PLACE_A, _envelope(["1", "2", "3"])),
            (PLACE_B, _envelope(["4", "5", "6"])),
        ],
        limit=2,
    )
    assert [row["job_id"] for row in merged["results"]] == ["1", "4"], merged
    assert merged["capped"] is True, merged
    # BOTH places survive the trim. Concatenation would have returned 1 and 2.
    assert {row["found_in"] for row in merged["results"]} == {PLACE_A, PLACE_B}


def test_order_within_a_place_is_linkedins_own():
    merged = jobfilter.merge_location_reads(
        [(PLACE_A, _envelope(["1", "2", "3"]))], limit=25
    )
    assert [row["job_id"] for row in merged["results"]] == ["1", "2", "3"]


def test_a_posting_answering_two_places_is_returned_once():
    """A remote role legitimately matches every city, and counting it per city
    would inflate the shortlist."""
    merged = jobfilter.merge_location_reads(
        [
            (PLACE_A, _envelope(["1", "2"])),
            (PLACE_B, _envelope(["2", "3"])),
        ],
        limit=25,
    )
    ids = [row["job_id"] for row in merged["results"]]
    assert ids.count("2") == 1, ids
    assert merged["count"] == 3, merged
    assert merged["searches"][1]["already_seen"] == 1, merged["searches"]
    # The place that saw it FIRST is the one recorded.
    found_in = {row["job_id"]: row["found_in"] for row in merged["results"]}
    assert found_in["2"] == PLACE_A, found_in


def test_a_row_with_no_job_id_is_kept_and_counted_as_unkeyed():
    """The de-dupe says what it could not speak about rather than staying
    silent about it."""
    envelope = _envelope(["1"])
    envelope["results"].append({"title": "A posting with no id", "location": "Remote"})
    envelope["count"] = 2
    envelope["page_had"] = 2
    merged = jobfilter.merge_location_reads([(PLACE_A, envelope)], limit=25)
    assert merged["count"] == 2, merged
    assert merged["searches"][0]["unkeyed"] == 1, merged["searches"]


def test_every_place_is_accounted_for_even_when_it_returned_nothing():
    """A place that gave zero postings still gets a row in ``searches``.

    This is the half a short merged list cannot supply on its own: three
    places returning 7, 0 and 0 and three places returning 3, 2 and 2 both
    produce seven rows, and only ``searches`` tells them apart.
    """
    merged = jobfilter.merge_location_reads(
        [
            (PLACE_A, _envelope(["1", "2"])),
            (PLACE_B, _envelope([])),
            (PLACE_C, _envelope(["3"])),
        ],
        limit=25,
    )
    assert [entry["location"] for entry in merged["searches"]] == [
        PLACE_A,
        PLACE_B,
        PLACE_C,
    ]
    assert merged["searches"][1]["page_had"] == 0, merged["searches"]
    assert merged["searches"][1]["in_results"] == 0, merged["searches"]
    assert merged["pages_loaded"] == 3, merged


def test_page_had_is_the_sum_across_every_load():
    merged = jobfilter.merge_location_reads(
        [
            (PLACE_A, _envelope(["1"], page_had=7)),
            (PLACE_B, _envelope(["2"], page_had=5)),
        ],
        limit=25,
    )
    assert merged["page_had"] == 12, merged


def test_unparsed_rows_appears_only_when_something_was_dropped():
    clean = jobfilter.merge_location_reads(
        [(PLACE_A, _envelope(["1"]))], limit=25
    )
    assert "unparsed_rows" not in clean, clean
    dirty_envelope = _envelope(["1"])
    dirty_envelope["unparsed_rows"] = 2
    dirty = jobfilter.merge_location_reads([(PLACE_A, dirty_envelope)], limit=25)
    assert dirty["unparsed_rows"] == 2, dirty


# ---------------------------------------------------------------------------
# 4. END TO END THROUGH THE TOOL, because the merge being right and the tool
#    calling it are two different claims.
# ---------------------------------------------------------------------------


async def test_the_tool_merges_two_places_and_labels_every_row(drive):
    page = PagePerLoad([_cards("4111222401"), _cards("4111222402", "4111222403")])
    navigations = drive(page)

    result = await linkedin_search_jobs(
        keywords="node.js engineer", locations=f"{PLACE_A}{SEP}{PLACE_B}"
    )

    assert "error" not in result, result
    assert len(navigations) == 2, navigations
    assert result["count"] == 3, result
    assert result["query"]["locations"] == [PLACE_A, PLACE_B], result["query"]
    assert {row["found_in"] for row in result["results"]} == {PLACE_A, PLACE_B}
    assert [entry["location"] for entry in result["searches"]] == [PLACE_A, PLACE_B]


async def test_the_fan_out_note_says_it_is_not_a_cross_location_ranking(drive):
    """The one claim a caller could reasonably get wrong, said out loud.

    Someone comparing this against LinkedIn's own multi-location search will
    see different postings. The reason is structural -- no request named two
    places -- and if the result does not say so, the difference reads as this
    reader being broken.
    """
    page = PagePerLoad([_cards("4111222411"), _cards("4111222412")])
    drive(page)

    result = await linkedin_search_jobs(
        keywords="node.js engineer", locations=f"{PLACE_A}{SEP}{PLACE_B}"
    )

    note = result.get("note", "")
    assert note, result
    assert "cross-location" in note, note
    assert "searches" in note, note


@pytest.mark.parametrize(
    "kwargs",
    [
        {"locations": PLACE_A},
        {"locations": f"{SEP}{SEP}"},
        {"location": PLACE_A, "locations": f"{PLACE_B}{SEP}{PLACE_C}"},
    ],
    ids=["one-place", "separators-only", "both-arguments"],
)
async def test_every_refusal_reaches_the_caller_as_bad_argument(drive, kwargs):
    """A refusal has to arrive as ``bad_argument``, never as ``unexpected``.

    ``linkedin_search_jobs``'s body sits inside ``except Exception -> _error``,
    and this package has already recorded what that costs: a table that stopped
    matching its signature returned ``{"error": "unexpected", "message":
    "KeyError: ..."}`` with no page load -- quieter than a crash and easy to
    read as a transient fault. A plan that raised instead of returning a
    verdict would look exactly like that.
    """
    page = FakePage(evaluate_result=_cards("4111222421"))
    drive(page)
    result = await linkedin_search_jobs(keywords="node.js engineer", **kwargs)
    assert result["error"] == "bad_argument", result
    assert "message" in result and result["message"], result
