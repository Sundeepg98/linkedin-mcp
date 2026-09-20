"""THE CONTROLS for wave 38's two firing probes. Every one plants a defect.

## WHY THIS FILE EXISTS

The two probes in this wave decide whether a census row may move from
`COVERED-UNFIRED` to `COVERED-PROVEN`. That makes their verdict functions
INSTRUMENTS, and this repository's register admits an instrument only if it has
been SHOWN FAILING -- a check that cannot fail certifies nothing, and a library
of such checks is worse than none because it manufactures confidence at scale.

So every test below plants the specific defect that would have let the wave
INFLATE its own count, and requires the instrument to refuse.

## THE TWO FAILURE MODES THESE GUARD

1. **A DEAD READER LOOKS LIKE A WORKING ONE OVER A FLAT SAMPLE.**
   `verified_job` is `bool(markers.get("verified"))`. A reader whose selector
   has rotted returns False for every posting on earth. Over a sample of
   unverified jobs that is indistinguishable from a correct reader, and
   "the field came back on 11 of 11 postings" reads as success.
   `_verdict` must answer NEVER-TRUE and `_bankable` must refuse.

2. **A DROPPED FILTER RETURNS A PERFECTLY HEALTHY RESULT SET.**
   A query parameter LinkedIn ignores, or one appended to the wrong key,
   returns the UNFILTERED results. Seven rows come back and nothing is wrong
   on the surface. `filters._verdict` must answer NO-EFFECT and refuse.

The third guarded mode is the one this wave actually committed: an instrument
too crude to tell a consumed counter from a re-render, which SHOUTED a false
positive. See `test_consumption_is_unknown_when_either_end_is_unreadable`.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"


def _load(name: str):
    """Import a probe by path; `scripts/` is not a package."""
    path = SCRIPTS / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(SCRIPTS))
    spec.loader.exec_module(module)
    return module


insights = _load("_probe_unfired_job_detail_insights")
filters = _load("_probe_unfired_job_search_filters")


# --------------------------------------------------------------------------
# MODE 1 -- the dead reader. The planted defect is a FLAT sample.
# --------------------------------------------------------------------------

def test_a_field_false_on_every_posting_is_refused_not_banked():
    """THE PLANTED DEFECT: a reader that returns False 11 times out of 11.

    This is what a rotted selector produces, and it is the single most
    flattering-looking failure available to this wave: the field is present,
    the dict is well formed, nothing raised. If `_verdict` answered anything
    bankable here, four census rows would have been banked on a dead reader.
    """
    assert insights._verdict(true_n=0, false_n=11, absent_n=0) == "NEVER-TRUE"
    assert "NOT BANKABLE" in insights._bankable("NEVER-TRUE")


def test_a_field_that_never_arrives_is_refused():
    """THE PLANTED DEFECT: the key is missing from every result."""
    assert insights._verdict(true_n=0, false_n=0, absent_n=11) == "ABSENT"
    assert "NOT BANKABLE" in insights._bankable("ABSENT")


def test_an_empty_sample_cannot_bank_anything():
    """THE PLANTED DEFECT: zero postings read, which must not read as a pass."""
    assert insights._verdict(true_n=0, false_n=0, absent_n=0) == "NO-SAMPLE"
    assert "NOT BANKABLE" in insights._bankable("NO-SAMPLE")


def test_a_discriminating_field_is_the_only_thing_that_banks():
    """THE POSITIVE CONTROL. Without it the refusals above prove only that
    this function refuses everything, which certifies nothing either."""
    assert insights._verdict(true_n=5, false_n=6, absent_n=0) == "OBSERVED-BOTH"
    assert insights._bankable("OBSERVED-BOTH") == "BANKABLE"
    assert insights._verdict(true_n=9, false_n=0, absent_n=0) == "OBSERVED-TRUE"
    assert insights._bankable("OBSERVED-TRUE") == "BANKABLE"


# --------------------------------------------------------------------------
# MODE 2 -- the dropped filter. The planted defect is IDENTICAL result sets.
# --------------------------------------------------------------------------

def test_a_filter_whose_every_value_returns_the_same_rows_is_refused():
    """THE PLANTED DEFECT: four filter values, one identical id set.

    That is exactly what a parameter LinkedIn ignores looks like. Each call
    succeeded and each returned rows, so any check keyed on "did it respond"
    passes. Five census rows hang on this refusal.
    """
    same = frozenset({"1", "2", "3"})
    verdict = filters._verdict([same, same, same, same], drift=0)
    assert verdict.startswith("NO-EFFECT")
    assert "NOT BANKABLE" in filters._bankable(verdict)


def test_a_difference_inside_the_drift_floor_is_refused():
    """THE PLANTED DEFECT: sets that differ only as much as noise already does.

    LinkedIn reshuffles results between two identical requests. A filter whose
    disagreement is within that floor has not been shown to do anything, and
    counting it would mean measuring the platform's churn and calling it a
    capability.
    """
    a = frozenset({"1", "2", "3"})
    b = frozenset({"1", "2", "4"})
    # a ^ b has two elements; a drift floor of 2 must swallow it.
    verdict = filters._verdict([a, b], drift=2)
    assert verdict.startswith("INDISTINGUISHABLE FROM DRIFT")
    assert "NOT BANKABLE" in filters._bankable(verdict)


def test_one_value_returning_rows_is_too_thin_to_judge():
    """THE PLANTED DEFECT: every value but one came back empty."""
    verdict = filters._verdict([frozenset({"1"}), frozenset()], drift=0)
    assert verdict.startswith("THIN")
    assert "NOT BANKABLE" in filters._bankable(verdict)


def test_a_filter_that_moves_results_past_the_drift_floor_banks():
    """THE POSITIVE CONTROL for the filter verdict."""
    a = frozenset({"1", "2", "3"})
    b = frozenset({"7", "8", "9"})
    verdict = filters._verdict([a, b], drift=1)
    assert verdict.startswith("DISCRIMINATES")
    assert filters._bankable(verdict) == "BANKABLE"


# --------------------------------------------------------------------------
# MODE 3 -- the crude consumption check. THIS WAVE SHIPPED THIS DEFECT FIRST.
# --------------------------------------------------------------------------

def test_consumption_is_unknown_when_either_end_is_unreadable():
    """THE DEFECT THIS WAVE ACTUALLY COMMITTED, planted back as a control.

    The probe's first version compared `len(str(reading))` -- the character
    length of the badge dict's repr -- and on a run that opened four job
    postings reported "THE BADGE MOVED. Something was spent."

    It had not. `read_invitation_badge` leaves `label` None whenever the nav
    has not hydrated, so an unhydrated first read followed by a hydrated
    second read lengthens the repr by exactly the label. The reading below is
    that exact pair, and the instrument must now answer UNKNOWN.
    """
    unhydrated = {"links": 1, "badge_links": 0, "label": None, "error": None}
    hydrated = {"links": 1, "badge_links": 1, "label": "shaped", "error": None}
    assert filters._badge_state(unhydrated).startswith("UNREADABLE")
    assert filters._badge_state(hydrated) == "READABLE"
    verdict = filters._consumption(unhydrated, hydrated)
    assert verdict.startswith("UNKNOWN")
    # And it must NOT claim nothing was spent, which is the other half of the
    # error: silence and "nothing was consumed" are different claims.
    assert "nothing was spent" not in verdict.replace(
        "rather than saying nothing was spent", "")


def test_consumption_reports_a_real_move_when_both_ends_are_readable():
    """THE POSITIVE CONTROL: the check must still be able to say MOVED."""
    before = {"links": 1, "badge_links": 1, "label": "a", "error": None}
    after = {"links": 1, "badge_links": 1, "label": "b", "error": None}
    assert filters._consumption(before, after).startswith("THE BADGE MOVED")


def test_consumption_reports_no_move_when_the_labels_agree():
    before = {"links": 1, "badge_links": 1, "label": "a", "error": None}
    after = {"links": 1, "badge_links": 1, "label": "a", "error": None}
    assert "did not move" in filters._consumption(before, after)


def test_an_errored_reading_is_never_treated_as_a_zero_badge():
    """A reader that could not run must not look like a badge at zero."""
    errored = {"error": "TimeoutError"}
    good = {"links": 1, "badge_links": 1, "label": "a", "error": None}
    assert filters._badge_state(errored).startswith("UNREADABLE")
    assert filters._consumption(errored, good).startswith("UNKNOWN")


# --------------------------------------------------------------------------
# MODE 4 -- THE PANEL JUDGEMENT. Two of these branches exist only because a
# ratchet caught them missing, so each is shown FIRING here rather than
# assumed. A branch nobody can reach is the same defect as a check that
# cannot fail.
# --------------------------------------------------------------------------

_ALL_ZERO = {"percentile": 0, "rank": 0, "skill": 0, "%": 0}


def test_an_empty_sample_refuses_to_judge_either_row():
    """THE PLANTED DEFECT: zero panels read, every tally therefore zero.

    Without this branch the all-zero tallies fall into each `else` and the
    probe prints NOT DELIVERED -- a negative claim about LinkedIn drawn from
    nothing observed. It must decline to judge instead.
    """
    lines = "\n".join(insights.judge_panels(0, dict(_ALL_ZERO), 0))
    assert "NOT JUDGED" in lines
    assert "OBSERVED NOTHING" in lines
    assert "NOT DELIVERED" not in lines, (
        "an empty sample produced a NOT DELIVERED verdict: " + lines
    )


def test_a_missing_percentile_with_no_gated_control_is_not_blamed_on_premium():
    """THE PLANTED DEFECT: no percentile AND the gated control never seen.

    The ordinary reading blames Premium gating. With zero sightings of the
    control that attribution is unobserved, and stating it would name a
    mechanism this run never saw.
    """
    lines = "\n".join(insights.judge_panels(11, dict(_ALL_ZERO), 0))
    assert "THE USUAL EXPLANATION DOES NOT" in lines
    assert "CANNOT be attributed to Premium gating" in lines


def test_the_ordinary_reading_still_blames_premium_when_it_was_seen():
    """THE POSITIVE CONTROL, and it is the shape the real run produced:
    11 panels read, no percentile token, the gated control drawn on 7."""
    lines = "\n".join(insights.judge_panels(11, dict(_ALL_ZERO), 7))
    assert "NOT DELIVERED" in lines
    assert "sits behind the" in lines
    assert "7 of 11" in lines
    assert "THE USUAL EXPLANATION DOES NOT" not in lines


def test_a_percentile_token_stops_the_row_being_written_off():
    """The other direction: if the token IS there, do not print NOT DELIVERED."""
    hits = dict(_ALL_ZERO)
    hits["percentile"] = 3
    lines = "\n".join(insights.judge_panels(11, hits, 7))
    assert "inspect before banking" in lines
    assert "NOT DELIVERED" not in lines.split("J 122")[0]


def test_a_skills_token_stops_the_partial_verdict():
    hits = dict(_ALL_ZERO)
    hits["skill"] = 2
    lines = "\n".join(insights.judge_panels(11, hits, 7))
    assert "a skills token IS present" in lines
    assert "PARTIAL" not in lines


# --------------------------------------------------------------------------
# The two probes must agree, because they carry the same three functions.
# --------------------------------------------------------------------------

def test_the_two_probes_agree_on_what_a_badge_state_is():
    """Copied logic drifts. If these ever disagree, one probe is lying."""
    for reading in (
        {"links": 1, "badge_links": 0, "label": None, "error": None},
        {"links": 1, "badge_links": 1, "label": "x", "error": None},
        {"error": "TimeoutError"},
    ):
        assert insights._badge_state(reading) == filters._badge_state(reading)
