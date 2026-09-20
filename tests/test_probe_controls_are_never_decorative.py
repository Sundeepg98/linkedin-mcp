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

``test_probe_corpus_has_no_new_decorative_control`` is the ratchet against
the real corpus: it loads ``scripts/probe_controls_known_decorative_
baseline.json`` (129 entries, generated from the 2026-09-20 census) and
fails only on a finding NOT already in that baseline -- a newly introduced
decorative control. It does NOT require the baseline to shrink as old
findings get fixed (that file's own header explains why: matching is on
(file, function, variable), and removing a fixed entry is encouraged but
optional). This is deliberately looser than an exact-count pin: multiple
unrelated waves add new probe files to this corpus daily, and an exact
global count would fail on someone else's unrelated addition as often as it
would fail on a real regression.
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


def test_probe_corpus_has_no_new_decorative_control():
    """The ratchet. Fails only on a finding not already in the pinned
    baseline (129 entries, 2026-09-20) -- i.e. only on a NEW instance of
    this defect, never on the pre-existing, disclosed backlog a separate
    fixer is working through."""
    baseline_doc = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    known = {
        (e["file"], e["function"], e["variable"]) for e in baseline_doc["entries"]
    }

    results = detector.scan_corpus()
    new_findings = []
    for r in results:
        for f in r.get("findings", []):
            key = (r["file"], f["function"], f["variable"])
            if key not in known:
                new_findings.append(
                    f"{r['file']}:{f['line']} {f['function']}() -> {f['variable']!r} "
                    f"(markers: {', '.join(f['markers'])})"
                )

    assert not new_findings, (
        "NEW never-branched probe control(s) not in "
        "scripts/probe_controls_known_decorative_baseline.json:\n  "
        + "\n  ".join(new_findings)
        + "\n\nEither branch on the control's result, or -- if this is a "
        "genuinely decorative reading that was reviewed and accepted -- add "
        "it to the baseline file with a one-line reason."
    )


def test_baseline_file_is_well_formed():
    """A baseline that silently stops parsing would make the ratchet test
    above vacuously pass on everything -- worth its own small check."""
    baseline_doc = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    assert baseline_doc["count"] == len(baseline_doc["entries"])
    assert baseline_doc["count"] > 0
    for entry in baseline_doc["entries"]:
        assert set(entry) == {"file", "function", "variable", "line"}
