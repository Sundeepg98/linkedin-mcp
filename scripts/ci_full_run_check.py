#!/usr/bin/env python3
"""Assert that a CI run executed EVERY test the checkout contains.

WHY THIS FILE EXISTS. A suite that reports "passed" while quietly running a
subset of itself is the worst possible gate: it is greener than no gate at all
and it certifies less. The two ways a Python suite shrinks silently are

  1. DESELECTION -- ``-m "not browser"``, ``--ignore=...``, ``--deselect``.
     Deselected tests do not appear in the junit report at all, so counting
     what the report holds can never notice them.
  2. ENVIRONMENT SKIPS -- ``pytest.skip()`` inside a test because some
     resource is not present on this machine. These DO appear in the report,
     marked skipped, and a human reading "684 passed, 79 skipped" in a
     collapsed log reads the first number.

Neither shows up in a green check mark. So this script compares two numbers
that come from the SAME checkout and must therefore agree:

  * COLLECTED -- what ``pytest --collect-only`` says exists;
  * RAN -- what the junit report says was executed.

A gap between them is a deselection. A non-zero skip count is a test that
decided it could not run here. Both fail this check, and both print the exact
number rather than a summary word.

THE NUMBER IS ALSO PUBLISHED, not just asserted: the line goes to stdout and
to ``$GITHUB_STEP_SUMMARY``, so the run's summary page carries the count
whether the check passes or fails.

WHY SKIPS ARE A HARD FAILURE HERE RATHER THAN A WARNING. The workflow that
calls this script installs whatever the suite needs in order to skip nothing:
the jobcore sibling the vendored-drift guards walk up to find, and -- in the
repository whose suite launches one -- the chromium binary. A skip therefore
means one of those arrangements silently stopped working, which is precisely
the drift-guard-that-never-ran failure this whole gate exists to prevent. If a
future test genuinely must skip somewhere, that is a decision worth making in
the open, with a reason attached; it is not something a runner should be
allowed to decide quietly on a Tuesday.

THIS FILE IS DUPLICATED, in linkedin and in ats-jobs, and there is no drift
guard on it. That is a stated cost rather than an oversight: the vendoring
ceremony those repositories run for jobcore's modules (a header, a pinned sha
and a byte-comparison test) is worth its weight for code the servers execute,
and is not worth it for a CI helper that neither server imports. The two
copies are byte-identical today, so `diff` is the whole instrument.

USAGE
    python scripts/ci_full_run_check.py <collected.txt> <junit.xml>

where collected.txt is the stdout of ``pytest --collect-only -q``.

SHOWN FAILING. Run it against a junit report from a deselected run (for
instance ``pytest --ignore=tests/test_browser.py --junitxml=...``) paired with
a full ``--collect-only`` and it exits 1 naming the gap. A check that has
never been shown failing certifies nothing.
"""

from __future__ import annotations

import os
import re
import sys

# stdlib ElementTree, deliberately, and not defusedxml. The only document this
# ever parses is the junit report pytest itself wrote seconds earlier in the
# same job from a checkout this workflow controls -- there is no untrusted
# input path into it. Pulling defusedxml in would add a dependency to a repo
# whose requirements.txt justifies every pin in prose, to harden a parser that
# is not exposed to an attacker. If this script is ever pointed at a report
# from somewhere else, that trade changes and so should this line.
import xml.etree.ElementTree as ET

#: pytest 8 ends ``--collect-only -q`` with a line like "684 tests collected
#: in 0.42s"; with collection errors it reads "3 tests collected, 4 errors".
#: Anchored on the count and the word, not on the tail, so either form parses.
_COLLECTED = re.compile(r"(\d+)\s+tests?\s+collected")


def collected_count(path: str) -> int:
    text = open(path, encoding="utf-8", errors="replace").read()
    matches = _COLLECTED.findall(text)
    if not matches:
        sys.exit(
            f"FAIL: {path} holds no 'N tests collected' line, so how many "
            f"tests exist in this checkout is unknown. Collection itself "
            f"probably failed; the file is reproduced below.\n\n{text[-4000:]}"
        )
    # Last match: a rerun or a warning block can put earlier numbers above it.
    return int(matches[-1])


def junit_totals(path: str) -> dict:
    root = ET.parse(path).getroot()
    # pytest writes <testsuites><testsuite .../></testsuites>; older shapes
    # put the attributes on the root itself. Accept both rather than assume.
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        sys.exit(f"FAIL: {path} contains no <testsuite> element")
    return {
        key: int(suite.get(key, 0))
        for key in ("tests", "failures", "errors", "skipped")
    }


def publish(line: str) -> None:
    print(line, flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def main(argv: list) -> int:
    if len(argv) != 3:
        sys.exit(f"usage: {argv[0]} <collected.txt> <junit.xml>")

    collected = collected_count(argv[1])
    totals = junit_totals(argv[2])
    ran = totals["tests"]
    skipped = totals["skipped"]
    executed = ran - skipped

    publish(
        f"collected {collected} | reported {ran} | executed {executed} | "
        f"skipped {skipped} | failed {totals['failures']} | "
        f"errors {totals['errors']}"
    )

    problems = []
    if collected == 0:
        problems.append("collection found ZERO tests, so nothing was gated")
    if ran != collected:
        problems.append(
            f"{collected - ran} test(s) were DESELECTED: collection found "
            f"{collected} but only {ran} reached the report. A deselected "
            f"test leaves no trace in junit, which is why this is compared "
            f"against collection rather than read off the report"
        )
    if skipped:
        problems.append(
            f"{skipped} test(s) SKIPPED. The workflow installs what this "
            f"suite needs in order to skip nothing, so a skip means one of "
            f"those arrangements stopped working -- most often the jobcore "
            f"sibling clone the drift guards look for. Run with -rs to see "
            f"which tests and why"
        )

    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1

    print(f"OK: all {collected} collected tests ran, none skipped, none deselected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
