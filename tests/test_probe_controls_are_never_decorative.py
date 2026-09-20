"""Guard: no probe self-check may be computed, printed, and never branched on.

WHAT THIS TESTS, and why the fixtures are inline text rather than a file
reference. ``scripts/detect_unbranched_probe_controls.py`` (see its own
docstring for the full method) finds probe "controls" -- must-fire and
must-stay-silent self-checks -- that are printed but never gate anything.
The real-world case that motivated this: ``scripts/_probe_events_surface_
shape.py`` printed ``CONTROL, must stay silent: {silent} {'PASS' if
silent == 0 else 'FAIL'}`` and never branched on ``silent`` -- fixed in
commit ``2fba253`` (``_audit/INSTRUMENTS.md`` entry 24). That real file will
keep changing as this repo evolves, so pinning a test to its git history
would eventually test nothing; the two fixtures below are the SAME SHAPE,
frozen, so this test keeps meaning what it says regardless of what happens
to the file that inspired it.

``test_detector_flags_...`` and ``test_detector_does_not_flag_...`` are the
SHOWN-FAILING pair `_audit/INSTRUMENTS.md` requires before an instrument is
trusted: same shape, one broken and one fixed, one variable name apart
(adding exactly the ``if silent: ...`` branch), opposite verdicts. Together
they prove the detector discriminates rather than merely asserting.

``test_probe_corpus_baseline_is_an_exact_mapping`` is the ratchet against
the real corpus, and it is a TWO-WAY ratchet: it loads ``scripts/
probe_controls_known_decorative_baseline.json`` (129 entries, generated from
the 2026-09-20 census) and fails on EITHER a finding not already in that
baseline (a newly introduced decorative control) OR a baseline entry the
detector no longer finds live (fixed, or reclassified -- either way the
entry is now stale and must be corrected, never left in place). This
mirrors ``tests/test_page_text_is_never_printed.py``'s ``KNOWN_TEXT_SINKS``,
this repository's established pattern for the same shape: "asserted as an
EXACT MAPPING, so it cannot rot in either direction... the documentation of
a defect may not outlive the defect." An earlier version of this test only
checked the GAINED direction, which a same-day review on this branch named
correctly: a one-way ratchet lets a fixed finding sit in the baseline
forever with nothing prompting anyone to remove it. The corpus-count
concern that motivated the one-way version still holds and is handled
differently here: matching is on (file, function, variable), not a global
total, so an unrelated wave adding a brand new probe file changes nothing
about this baseline's 129 entries and cannot trip either direction of this
check -- only a change to one of THESE 129 specific sites can.

THE BASELINE CARRIES REASONS NOW, and only where one was actually derived.
`scripts/probe_controls_known_decorative_baseline.json` gained an OPTIONAL
`reason` string on 2026-09-20 (the five-under-banked wave), which is the shape
`_audit/INSTRUMENTS.md` 34.8 asked for after the premium-four integration had
to argue four specimens in a file with nowhere to say so: *"a triage table
whose entries cannot carry their triage is a census wearing a ratchet's name"*.
Ten entries carry one; the rest do not, and that difference is the point --
an unreasoned entry is visibly untriaged rather than silently assumed
reviewed. `test_baseline_file_is_well_formed` therefore asserts the field's
SHAPE and that it has not been wiped, never a count.

Two entries are a KNOWN OPEN QUESTION rather than a settled false positive,
recorded here instead of resolved unilaterally: the same review disputed
`_probe_events_surface_shape.py`'s `rows_with_any` and `note` as "display
values, not controls," and `hits` as "correctly not branched, because the
must-fire control was hoisted above it and IS branched" -- i.e. a
semantically-equivalent sibling variable already gates the same condition.
That is a claim about the DETECTOR'S marker vocabulary conflating a
self-check with LinkedIn UI-control terminology (this census's own
section 6 raised the identical ambiguity), not about the code having
changed, and re-running the detector against the live file confirms the
code is unchanged and these three still mechanically qualify as findings
under this file's stated rules. Deciding whether to narrow those rules is
left to whoever owns that call next; this test only asserts what the
detector currently says, correctly, in both directions.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import detect_unbranched_probe_controls as detector  # noqa: E402

BASELINE_PATH = REPO / "scripts" / "probe_controls_known_decorative_baseline.json"

#: The real defect's shape, reduced to a minimal standalone module. Modeled
#: on scripts/_probe_events_surface_shape.py as it was before commit
#: 2fba253 -- not copied verbatim (that file is much longer), but the exact
#: same anatomy: a must-stay-silent control, computed, printed with the
#: literal words PASS/FAIL, and never branched on.
BROKEN_FIXTURE = '''
def main():
    silent = len(IMPOSSIBLE.findall(html))
    print(f"--- CONTROL, must stay silent: {silent} "
          f"{'PASS' if silent == 0 else 'FAIL'}")
    return 0
'''

#: The identical shape with the ONE thing added that the real fix added:
#: a branch that actually consumes the control's result.
FIXED_FIXTURE = '''
def main():
    silent = len(IMPOSSIBLE.findall(html))
    print(f"--- CONTROL, must stay silent: {silent} "
          f"{'PASS' if silent == 0 else 'FAIL'}")
    if silent:
        print("VOID.")
        return 1
    return 0
'''

#: The calibration's other documented shape: a needle loop where the `if`
#: branches on a DIFFERENT variable (`needle`) than the one printed (`hits`),
#: so `hits` itself is still never branched on even though an `if` sits
#: right next to it. This is the shape a naive "is there an if nearby"
#: check would wrongly clear.
NEEDLE_LOOP_FIXTURE = '''
def main():
    for needle in SELF_SCOPED_NEEDLES:
        hits = sum(1 for href in hrefs if needle in href)
        note = ""
        if needle == "/events/":
            note = "  <- must fire"
        print(f"    {hits:>5}  {needle}{note}")
'''


def _findings_by_variable(source: str) -> dict[str, dict]:
    result = detector.analyse_source(source, filename="<fixture>")
    assert result["parse_ok"], result.get("error")
    return {f["variable"]: f for f in result["findings"]}


def _branched_by_variable(source: str) -> dict[str, dict]:
    result = detector.analyse_source(source, filename="<fixture>")
    assert result["parse_ok"], result.get("error")
    return {f["variable"]: f for f in result["branched_controls"]}


def test_detector_flags_a_never_branched_control():
    """SHOWN FAILING, half 1: the broken shape must be caught."""
    findings = _findings_by_variable(BROKEN_FIXTURE)
    assert "silent" in findings, (
        "the detector did not flag a control that is computed, printed with "
        "PASS/FAIL text, and never branched on -- it would pass a real "
        "defect through silently"
    )
    assert findings["silent"]["num_non_sink_loads"] == 0


def test_detector_does_not_flag_a_correctly_branched_control():
    """SHOWN FAILING, half 2 (the discrimination proof): the SAME shape,
    with only the branch added, must NOT be flagged. Same file, one
    variable name apart, opposite verdicts -- if this failed, the detector
    would be asserting a fixed answer rather than reading content."""
    findings = _findings_by_variable(FIXED_FIXTURE)
    assert "silent" not in findings, (
        "the detector flagged a control that IS branched on "
        "(`if silent: ...; return 1`) -- it cannot tell a repaired control "
        "from a live one, which makes every finding it reports suspect"
    )
    branched = _branched_by_variable(FIXED_FIXTURE)
    assert "silent" in branched
    assert branched["silent"]["num_non_sink_loads"] >= 1


def test_detector_sees_past_an_if_that_branches_on_a_different_variable():
    """The documented harder shape: an `if` sits right beside the print,
    but it branches on `needle`, not on `hits`, so `hits` is still a
    finding. A detector that credits ANY nearby `if` as a branch would
    wrongly clear this."""
    findings = _findings_by_variable(NEEDLE_LOOP_FIXTURE)
    assert "hits" in findings, (
        "a nearby `if` that tests a different variable must not be "
        "credited as branching on this one"
    )


def test_probe_corpus_baseline_is_an_exact_mapping():
    """The two-way ratchet -- GAINED and LOST, named separately because the
    two directions need opposite responses (same message shape as
    KNOWN_TEXT_SINKS's own test, deliberately)."""
    baseline_doc = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    known = {
        (e["file"], e["function"], e["variable"]) for e in baseline_doc["entries"]
    }

    results = detector.scan_corpus()
    live: dict[tuple[str, str, str], dict] = {}
    for r in results:
        for f in r.get("findings", []):
            live[(r["file"], f["function"], f["variable"])] = f

    gained = sorted(
        f"{file}:{f['line']} {func}() -> {var!r} (markers: {', '.join(f['markers'])})"
        for (file, func, var), f in live.items()
        if (file, func, var) not in known
    )
    lost = sorted(
        f"{e['file']}:{e['line']} {e['function']}() -> {e['variable']!r}"
        for e in baseline_doc["entries"]
        if (e["file"], e["function"], e["variable"]) not in live
    )

    assert not gained and not lost, (
        "scripts/probe_controls_known_decorative_baseline.json has drifted "
        "from what the detector currently finds.\n"
        "  GAINED (a NEW never-branched control -- do NOT add it here to "
        "clear the red; branch on its result, or if it is a genuinely "
        "decorative reading that was reviewed and accepted, add it to the "
        "baseline with a one-line reason):\n    "
        + ("\n    ".join(gained) or "(none)")
        + "\n  LOST (the detector no longer finds this one -- fixed, or "
        "reclassified; correct the baseline entry, because the "
        "documentation of a defect may not outlive the defect):\n    "
        + ("\n    ".join(lost) or "(none)")
    )


def test_baseline_file_is_well_formed():
    """A baseline that silently stops parsing would make the ratchet test
    above vacuously pass on everything -- worth its own small check."""
    baseline_doc = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    assert baseline_doc["count"] == len(baseline_doc["entries"])
    assert baseline_doc["count"] > 0
    reasoned = 0
    for entry in baseline_doc["entries"]:
        assert {"file", "function", "variable", "line"} <= set(entry)
        assert set(entry) <= {"file", "function", "variable", "line", "reason"}
        if "reason" in entry:
            assert isinstance(entry["reason"], str) and entry["reason"].strip()
            reasoned += 1
    # A REASON IS OPTIONAL AND ITS ABSENCE IS INFORMATION. This asserts only
    # that the field, where present, says something -- and that the file has
    # not been REGENERATED from the detector, which emits no reasons and would
    # silently erase every triage ever recorded here. There is deliberately NO
    # floor on how many entries carry one: a floor is an incentive to write
    # reasons in bulk, which is the rubber stamp `_audit/INSTRUMENTS.md` 34.8
    # warned about when it asked for this field.
    assert reasoned >= 1, (
        "no entry carries a `reason`. Either the field was dropped, or this "
        "file was regenerated straight from the detector -- which erases the "
        "triage that distinguishes a reviewed reading from a rubber stamp. "
        "Re-apply the reasons rather than shipping a bare census."
    )
