"""Prove the staleness arms bite in OPPOSITE directions. Run, do not trust.

WHY THIS EXISTS. On 2026-09-19 ``_staleness`` was changed from comparing
COMMIT IDENTITY to comparing BUILD IDENTITY -- the bytes of the
``linkedin_server`` modules this process actually imported -- because a
neighbour committing ONE MARKDOWN FILE (+142 lines, zero Python) flipped a
write gate red on a process whose loaded Python was provably identical to
disk, and because the same detector had correctly stopped a write wave ten
minutes earlier on a delta that really did touch ``writes.py``.

Both behaviours had to survive. A suite that only ever passes cannot show
that, so this injects two mutations into ``server.py`` in turn and runs the
arms against each:

  MUTATION 1  "the old detector"   -- ``stale`` decided by the commit alone.
              ARM B must FAIL: the doc-only over-report is back.
              ARM A must PASS: the right stop still happens.

  MUTATION 2  "the quiet detector" -- ``stale`` hardwired False everywhere.
              ARM B passes (trivially), and ARM A and A2 must FAIL.

THE POINT IS THE DISAGREEMENT. If one mutation satisfied both arms, the arms
would not be independent and the suite would be decoration. A detector that
stops reporting a real staleness is far worse than one that over-reports, so
ARM A is the arm that may never be traded away.

``server.py`` is restored in a ``finally`` and the restoration is asserted.
Run it from anywhere:  python scripts/_check_staleness_arms_mutation_control.py
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = ROOT / "linkedin_server" / "server.py"
SUITE = "tests/test_stale_process_is_announced.py"

ARM_B = "test_arm_b_a_document_only_commit_does_not_make_a_process_stale"
ARM_A = "test_arm_a_a_python_delta_still_fires"
ARM_A2 = "test_arm_a2_an_uncommitted_edit_to_a_loaded_module_is_stale"
ARMS = (ARM_B, ARM_A, ARM_A2)

#: What each mutation must do to each arm. This is the assertion, not the
#: print-out: a control whose expectations live only in a human's reading of
#: the output is a control that silently stops controlling.
EXPECTED = {
    "MUTATION 1  the OLD detector (commit identity decides)": {
        ARM_B: "FAIL",
        ARM_A: "PASS",
    },
    "MUTATION 2  the QUIET detector (never fires)": {
        ARM_B: "PASS",
        ARM_A: "FAIL",
        ARM_A2: "FAIL",
    },
}

DECIDER = '    block["stale"] = BUILD_DIGEST != disk_digest\n'
MUTANTS = {
    "MUTATION 1  the OLD detector (commit identity decides)":
        '    block["stale"] = moved  # MUTANT\n',
    "MUTATION 2  the QUIET detector (never fires)":
        '    block["stale"] = False  # MUTANT\n',
}


def run_arms() -> dict[str, str]:
    """{arm: PASS|FAIL}, read off pytest's own failure lines."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", SUITE, "-q", "--tb=no",
         "-p", "no:cacheprovider"],
        cwd=ROOT, capture_output=True, text=True,
    )
    failed = set(re.findall(r"::(\w+)", proc.stdout + proc.stderr))
    return {arm: ("FAIL" if arm in failed else "PASS") for arm in ARMS}


def report(label: str, result: dict[str, str]) -> None:
    print("=" * 72)
    print(label)
    for arm, verdict in result.items():
        print("   %-5s %s" % (verdict, arm))


def main() -> int:
    original = TARGET.read_text(encoding="utf-8")
    if original.count(DECIDER) != 1:
        print("ANCHOR LOST: the staleness decider line is not where this "
              "control expects it. Fix this file before trusting the suite.")
        return 2

    problems: list[str] = []
    try:
        baseline = run_arms()
        report("BASELINE -- unmutated (every arm must pass)", baseline)
        for arm, verdict in baseline.items():
            if verdict != "PASS":
                problems.append("baseline: %s is %s" % (arm, verdict))

        for label, mutant in MUTANTS.items():
            body = original.replace(DECIDER, mutant)
            if "QUIET" in label:
                # The early returns set stale True on their own; a quiet
                # detector has to be quiet everywhere or it is not the mutant.
                body = body.replace('            block["stale"] = True\n',
                                    '            block["stale"] = False  # MUTANT\n')
                body = body.replace('                block["stale"] = True\n',
                                    '                block["stale"] = False  # MUTANT\n')
            TARGET.write_text(body, encoding="utf-8")
            print()
            result = run_arms()
            report(label, result)
            for arm, want in EXPECTED[label].items():
                if result[arm] != want:
                    problems.append(
                        "%s: %s was %s, expected %s"
                        % (label.split()[1], arm, result[arm], want)
                    )
    finally:
        TARGET.write_text(original, encoding="utf-8")

    if TARGET.read_text(encoding="utf-8") != original:
        print("RESTORATION FAILED -- server.py is not as it was found.")
        return 2

    print()
    restored = run_arms()
    report("RESTORED -- unmutated again", restored)
    for arm, verdict in restored.items():
        if verdict != "PASS":
            problems.append("after restore: %s is %s" % (arm, verdict))

    print()
    if problems:
        print("CONTROL FAILED:")
        for line in problems:
            print("  - " + line)
        return 1
    print("CONTROL PASSES: no single mutation satisfies both arms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
