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

AND ONE OF THEM ALREADY MUST, which is what scripts/ci_expected_skips.json is
for. tests/test_no_committed_identity.py's exact-value sweep needs
_audit/_sanitisation_key.json -- the de-anonymisation key for the committed
fixtures, gitignored on purpose and never to reach a public runner. It skips on
every machine but the operator's, so this check as originally written could
never pass in CI, on any cell, ever. That is the failure the sentence above
warns about arriving from the other direction: A GATE THAT CANNOT PASS IS
INDISTINGUISHABLE FROM ONE THAT HAS NOT PASSED YET, which is the opening line
of tests/test_prose_that_makes_a_claim.py. So a skip is tolerated ONLY when it
is named in that file with its reason written out, it is PRINTED on every run
including green ones, and everything else still fails -- named, not counted.

AN XFAIL IS NOT A SKIP, AND THIS FILE USED TO SAY IT WAS. Measured 2026-09-05
against a fully green serial run of the whole suite: 3655 passed, 4 skipped,
1 xfailed -- and this check exited 1, reporting FIVE skips. junit has one
element for both outcomes and separates them only by ``type``:
``pytest.skip`` for a test that decided it could not run here, and
``pytest.xfail`` for one that RAN, failed, and was expected to. The
``skipped=`` attribute on <testsuite> counts them together, so reading it made
a red build out of tests/test_click_is_not_its_own_evidence.py's deliberate
``xfail(strict=True)`` -- a marker whose whole purpose is to sit in the suite
until somebody fixes the defect it records. Every cell of the matrix would
have failed for it, on the first run this workflow ever had. So the two are
counted separately below, the xfail is reported rather than hidden, and only a
real skip fails the check. The argument above is untouched: it was always
about a test that COULD NOT RUN, which an xfail is not.

THIS FILE IS DUPLICATED, in linkedin and in ats-jobs, and there is no drift
guard on it. That is a stated cost rather than an oversight: the vendoring
ceremony those repositories run for jobcore's modules (a header, a pinned sha
and a byte-comparison test) is worth its weight for code the servers execute,
and is not worth it for a CI helper that neither server imports. The two
copies WERE byte-identical until the xfail correction above; ats-jobs has the
same bug and the same fix is owed to it, and until that lands `diff` reports a
difference that is a to-do rather than drift.

USAGE
    python scripts/ci_full_run_check.py <collected.txt> <junit.xml>

where collected.txt is the stdout of ``pytest --collect-only -q``.

SHOWN FAILING. Run it against a junit report from a deselected run (for
instance ``pytest --ignore=tests/test_browser.py --junitxml=...``) paired with
a full ``--collect-only`` and it exits 1 naming the gap. A check that has
never been shown failing certifies nothing.
"""

from __future__ import annotations

import json
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
    totals = {
        key: int(suite.get(key, 0))
        for key in ("tests", "failures", "errors", "skipped")
    }

    # The <skipped> ELEMENTS, split by type -- see the docstring. The attribute
    # is kept as a cross-check rather than discarded: if the elements and the
    # attribute disagree, this report is not the shape either number was read
    # off, and guessing which one to trust is how a gate ends up certifying
    # arithmetic instead of a run.
    kinds = []
    names = []
    for case in suite.iter("testcase"):
        for element in case.iter("skipped"):
            kind = element.get("type", "")
            kinds.append(kind)
            if kind != "pytest.xfail":
                names.append(f"{case.get('classname')}::{case.get('name')}")
    totals["xfailed"] = sum(1 for kind in kinds if kind == "pytest.xfail")
    totals["skipped"] = len(kinds) - totals["xfailed"]
    # NAMED, not counted. "4 test(s) skipped, run with -rs to see which" makes
    # the reader re-run a 27-minute suite to learn something the report in
    # front of them already holds; this repository has lost three rounds to
    # refusals that reported a count without the observations behind it.
    totals["skipped_tests"] = names
    if len(kinds) != int(suite.get("skipped", 0)):
        sys.exit(
            f"FAIL: {path} says skipped={suite.get('skipped')} but holds "
            f"{len(kinds)} <skipped> element(s)."
        )
    return totals


#: Skips that are DECLARED rather than discovered -- see the file's own _why.
EXPECTED_SKIPS_PATH = os.path.join(os.path.dirname(__file__), "ci_expected_skips.json")


def expected_skips(path: str = EXPECTED_SKIPS_PATH) -> dict:
    """The declared skips, or none if the file is absent.

    ABSENT IS NOT AN ERROR, because this script is byte-shared with ats-jobs
    and that repository has no such list. A missing file means the strict
    original behaviour: every skip fails.
    """
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["expected"]


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
    declared = expected_skips()
    ran = totals["tests"]
    skipped = totals["skipped"]
    executed = ran - skipped
    unexpected = [name for name in totals["skipped_tests"] if name not in declared]
    tolerated = [name for name in totals["skipped_tests"] if name in declared]

    publish(
        f"collected {collected} | reported {ran} | executed {executed} | "
        f"skipped {skipped} ({len(tolerated)} declared) | "
        f"xfailed {totals['xfailed']} | failed {totals['failures']} | "
        f"errors {totals['errors']}"
    )
    # Printed on every run, green or red. A tolerated skip that nobody ever
    # sees is a tolerated skip that outlives its reason.
    for name in tolerated:
        publish(f"  declared skip: {name}")

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
    if unexpected:
        named = "; ".join(unexpected[:20])
        if len(unexpected) > 20:
            named += f"; and {len(unexpected) - 20} more"
        problems.append(
            f"{len(unexpected)} test(s) SKIPPED and not declared. The workflow "
            f"installs what this suite needs in order to skip nothing, so a "
            f"skip means one of those arrangements stopped working -- most "
            f"often the jobcore sibling clone the drift guards look for. Run "
            f"with -rs for the reasons; the tests are: {named}. If one of them "
            f"is structural rather than broken, it belongs in "
            f"scripts/ci_expected_skips.json with the reason written out"
        )

    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1

    print(
        f"OK: all {collected} collected tests ran, none deselected, and the "
        f"only skips were the {len(tolerated)} declared in "
        f"scripts/ci_expected_skips.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
