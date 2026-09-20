"""Show the never-branched-control detector's OWN controls actually failing.

WHY THIS EXISTS. The rule this repository already carries is that a check
which cannot fail certifies nothing -- applied here to
``scripts/detect_unbranched_probe_controls.py`` and its pytest guard,
``tests/test_probe_controls_are_never_decorative.py``, before either is
trusted. A detector that always says "found a defect" is as useless as one
that never does; the only convincing proof is the SAME shape flipping
verdicts when, and only when, the underlying content changes.

FOUR DEMONSTRATIONS:

  A  the BROKEN fixture (computed, printed with PASS/FAIL text, never
     branched) must be FLAGGED. If it is not, the detector is decoration.
  B  the FIXED fixture -- the identical shape with only the branch added --
     must NOT be flagged. Same file, one variable name apart, opposite
     verdicts: this is what proves discrimination rather than assertion.
  C  the harder documented shape: an `if` sits beside the print but tests a
     DIFFERENT variable (`needle`, not `hits`). `hits` must still be
     flagged -- a detector that credits any nearby `if` as a branch would
     wrongly clear it.
  D  the RATCHET TEST must itself go RED when a real, currently-known-good
     baseline entry is removed from its view. This is done by calling the
     ratchet's own comparison with a baseline missing one real entry
     (in memory -- the tracked baseline file on disk is never touched), and
     showing that entry is reported as a "new" finding. A ratchet that
     cannot be tripped by ANYTHING is not a ratchet.

Run from the repo root with the venv interpreter. Prints a PASS/FAIL line
per demonstration and exits non-zero if any of them does not behave as
stated.

    ./venv/Scripts/python.exe scripts/_check_unbranched_control_detector_can_fail.py

RUN IT AGAIN whenever the marker list, the sink rule, or the window-climb
logic changes, and paste the output into the INSTRUMENTS.md entry for
whatever changed -- exactly the discipline this repo already asks of
``_check_tool_count_pin_control.py``.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import detect_unbranched_probe_controls as detector  # noqa: E402
import test_probe_controls_are_never_decorative as guard_test  # noqa: E402

FAILURES: list[str] = []


def _report(label: str, ok: bool) -> None:
    print("%-6s %s" % ("PASS" if ok else "FAIL", label))
    if not ok:
        FAILURES.append(label)


def main() -> int:
    # ---------------------------------------------------------------- A, B
    print("A/B. same shape, one branch apart -- must flip verdict")
    broken = detector.analyse_source(guard_test.BROKEN_FIXTURE, "<broken>")
    fixed = detector.analyse_source(guard_test.FIXED_FIXTURE, "<fixed>")
    broken_vars = {f["variable"] for f in broken["findings"]}
    fixed_vars = {f["variable"] for f in fixed["findings"]}
    fixed_branched_vars = {f["variable"] for f in fixed["branched_controls"]}
    _report("A: broken fixture flags `silent`", "silent" in broken_vars)
    _report("B: fixed fixture does NOT flag `silent`", "silent" not in fixed_vars)
    _report("B: fixed fixture's `silent` reads as correctly branched",
             "silent" in fixed_branched_vars)
    print()

    # ------------------------------------------------------------------- C
    print("C. an `if` beside the print that tests a DIFFERENT variable")
    needle_loop = detector.analyse_source(guard_test.NEEDLE_LOOP_FIXTURE, "<needle>")
    needle_vars = {f["variable"] for f in needle_loop["findings"]}
    _report("C: `hits` is still flagged despite the nearby `if needle == ...`",
             "hits" in needle_vars)
    print()

    # ------------------------------------------------------------------- D
    print("D. the ratchet itself must be able to go RED")
    baseline_doc = json.loads(guard_test.BASELINE_PATH.read_text(encoding="utf-8"))
    real_known = {(e["file"], e["function"], e["variable"]) for e in baseline_doc["entries"]}
    if not real_known:
        _report("D: baseline has at least one real entry to remove", False)
    else:
        removed = sorted(real_known)[0]
        crippled_known = real_known - {removed}
        results = detector.scan_corpus()
        new_findings = []
        for r in results:
            for f in r.get("findings", []):
                key = (r["file"], f["function"], f["variable"])
                if key not in crippled_known:
                    new_findings.append(key)
        _report(
            "D: removing one real baseline entry (%s) from view makes the "
            "ratchet report it as new" % (removed,),
            removed in new_findings,
        )
        # And the control on the control: with the FULL baseline restored,
        # that same entry must NOT be reported (else the corpus moved under
        # us mid-check, which would invalidate this demonstration).
        results_again = detector.scan_corpus()
        new_findings_full = []
        for r in results_again:
            for f in r.get("findings", []):
                key = (r["file"], f["function"], f["variable"])
                if key not in real_known:
                    new_findings_full.append(key)
        _report(
            "D control: with the FULL baseline, that entry is NOT reported",
            removed not in new_findings_full,
        )
    print()

    if FAILURES:
        print("DEMONSTRATION FAILED: %r" % (FAILURES,))
        return 1
    print("all demonstrations behaved as stated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
