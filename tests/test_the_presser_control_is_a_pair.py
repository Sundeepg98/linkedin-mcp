"""A negative control is evidence only beside a positive one that fired.

`scripts/_probe_analytics_controls_live.py` presses the controls a census
never presses, and its most likely output is a ZERO -- no disclosure on this
page. **A broken selector returns that same zero.** The probe's answer to that
is a control set run against synthetic documents, and the rule that makes the
set an instrument is:

    case B returning nothing means the PAGE hides nothing
    ONLY IF case A returned something IN THE SAME RUN.

THAT RULE WAS PROSE IN A DOCSTRING, WHICH IS WHERE THIS REPOSITORY KEEPS
FINDING ITS DEFECTS. Delete case A and the probe still runs, case B still
passes, and every zero it prints reads as evidence again -- silently, with no
test going red. This file is that rule made enforceable.

WHY THE TEST IS HERE AND THE SELECTOR'S OWN CONTROL IS NOT. `SELECT_JS` is
JavaScript. Every test in this package stubs `page.evaluate` and none executes
JS, so a pytest cannot exercise the selector at all -- it is shown failing in
the browser instead, by mutation, and that demonstration is recorded on the
probe. What CAN be tested here is the part that was factored out precisely so
that it could be: `control_verdict`, a pure function over case results.

**THE INPUT THAT MATTERS CANNOT BE PRODUCED BY A LIVE RUN ON DEMAND** -- case A
failing while case B passes. That is a broken detector wearing a clean
absence's clothes. It is the exact state the probe must refuse to report from,
and the only way to hand it to the verdict is to construct it.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
PROBE = REPO / "scripts" / "_probe_analytics_controls_live.py"


def _probe():
    """Load the probe as a module without running it.

    Imported by path rather than by package, because `scripts/` is not a
    package -- and by import rather than by AST, because the thing under test
    is the FUNCTION's behaviour and an AST reading would be a second
    implementation of it.
    """
    spec = importlib.util.spec_from_file_location("_probe_analytics", PROBE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _labels(module):
    return [label for label, _markup, _expected in module.CONTROL_CASES]


def test_the_case_table_has_both_arms():
    """A positive arm and a clean-absence arm must both exist.

    Not "some cases": the two specific shapes the rule is about. A table of
    six refusal cases would pass a naive "the table is non-empty" check and
    could not distinguish anything.
    """
    module = _probe()
    cases = module.CONTROL_CASES
    positive = [
        exp for _l, _m, exp in cases if exp["disclosure"] >= 1
    ]
    absence = [
        exp for _l, _m, exp in cases
        if exp["candidates"] == 0 and exp["denied"] == 0
    ]
    refusal = [exp for _l, _m, exp in cases if exp["denied"] >= 1]
    assert positive, "no case expects a disclosure to be FOUND"
    assert absence, "no case expects a clean absence"
    assert refusal, "no case exercises the act-word refusal arm"


def test_the_two_arms_differ_only_in_the_attribute_the_rule_is_about():
    """THE CONTRAST IS THE MEASUREMENT, so it must be a controlled one.

    If the positive and the absence document differ in their TEXT as well as
    in `aria-expanded`, then case B's zero could be caused by the text and the
    pair proves nothing about the attribute. Requiring the two markup strings
    to differ by exactly the attribute is what makes the contrast attributable.

    Stated as a property rather than as a string comparison against a literal,
    so rewording the button does not break the test while weakening the pair
    still does.
    """
    module = _probe()
    positive = [
        markup for _l, markup, exp in module.CONTROL_CASES
        if exp["disclosure"] >= 1 and exp["vocab"] == 0
    ]
    absence = [
        markup for _l, markup, exp in module.CONTROL_CASES
        if exp["candidates"] == 0 and exp["denied"] == 0
    ]
    assert positive and absence
    stripped = [m.replace(' aria-expanded="false"', "") for m in positive]
    assert any(s in absence for s in stripped), (
        "the positive document with its aria-expanded removed is not the "
        "absence document. The pair then differs in more than the attribute "
        "under test, and case B's zero is not attributable to it. "
        f"positive={positive} absence={absence}"
    )


@pytest.mark.parametrize(
    "results,valid,why",
    [
        ({"A": True, "B": True, "C": True}, True,
         "everything passed -- a zero from a live page means something"),
        ({"A": False, "B": True, "C": True}, False,
         "THE CASE THIS FILE EXISTS FOR: the detector did not fire on a "
         "document that certainly contains a disclosure, while the absence "
         "case passed. A live zero here is a fact about the selector"),
        ({"A": True, "B": False, "C": True}, False,
         "the absence arm broke -- the selector is finding things that are "
         "not there, which is a different defect and equally disqualifying"),
        ({"A": True, "B": True, "C": False}, False,
         "the refusal arm broke: an act word no longer stops a press"),
        ({}, False, "no results at all is not a pass"),
    ],
)
def test_the_verdict_refuses_unless_the_positive_arm_fired(results, valid, why):
    """Drive `control_verdict` with results a live run cannot be made to give.

    The labels here are SHORT STANDINS. `control_verdict` reads the real case
    table for which labels are positive, so the test below binds these to the
    real labels first -- otherwise this would be testing a dictionary lookup
    against names that do not exist, which is the shape of a test that cannot
    fail.
    """
    module = _probe()
    labels = _labels(module)
    positive_labels = [
        label for label, _m, exp in module.CONTROL_CASES
        if exp["disclosure"] >= 1
    ]
    absence_labels = [
        label for label, _m, exp in module.CONTROL_CASES
        if exp["candidates"] == 0 and exp["denied"] == 0
    ]
    refusal_labels = [
        label for label, _m, exp in module.CONTROL_CASES if exp["denied"] >= 1
    ]

    if not results:
        assert module.control_verdict({})["valid"] is False, why
        return

    real: dict[str, bool] = {label: True for label in labels}
    for label in positive_labels:
        real[label] = results["A"]
    for label in absence_labels:
        real[label] = results["B"]
    for label in refusal_labels:
        real[label] = results["C"]

    assert module.control_verdict(real)["valid"] is valid, why


def test_the_verdict_is_not_merely_all_ok():
    """`valid` must be stricter than "did everything pass".

    If `valid` were just `all(results.values())` this file would be checking
    `all()`. The distinguishing input is a run where the positive arm is
    ABSENT from the table rather than failing -- then `all_ok` is vacuously
    true over the remaining cases and only `positive_ok` can refuse.
    """
    module = _probe()
    labels = _labels(module)
    positive_labels = {
        label for label, _m, exp in module.CONTROL_CASES
        if exp["disclosure"] >= 1
    }
    without_positive = {
        label: True for label in labels if label not in positive_labels
    }
    verdict = module.control_verdict(without_positive)
    assert verdict["all_ok"] is True, (
        "every result present is True, so all_ok should be True -- if it is "
        "not, this test is measuring something other than what it says"
    )
    assert verdict["valid"] is False, (
        "a run that never reported the positive arm was accepted as valid. "
        "all_ok cannot see a case that is missing rather than failing; that "
        "is exactly why valid is a separate field"
    )
