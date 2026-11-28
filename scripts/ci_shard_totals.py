#!/usr/bin/env python3
"""The cross-shard half of the completeness gate: did every shard report back?

WHY THIS FILE EXISTS, and it is the whole reason sharding is allowed here at
all. ``scripts/ci_full_run_check.py`` proves that a SINGLE run executed every
test it collected. Split that run across six jobs and that check still passes
in each job while the suite as a whole runs a sixth of itself, because a job
that never started, was cancelled, died in its install step, or was quietly
dropped from the matrix leaves NOTHING BEHIND to be counted. The gap is
invisible from inside any surviving shard.

So the shards report, and something adds the reports up:

  * ``record`` runs in each shard job, reads that shard's plan and its junit
    report, and writes one small JSON file that is uploaded as an artifact. It
    runs with ``if: always()`` so a RED shard still says how many tests it ran
    -- a failing test is a different problem from a missing one, and conflating
    them loses the one nobody would otherwise look for.
  * ``verify`` runs in a final job that depends on every shard, downloads all
    the artifacts, and refuses unless, FOR EVERY MATRIX CELL, the shard indices
    present are exactly 0..n-1 and their executed tests sum to the number that
    cell collected.

WHAT MAKES THIS ABLE TO FAIL, which is the only property that makes it worth
having. Six independent ways, each with its own message and each exercised as
a control in tests/test_ci_shard.py:

  1. a report is MISSING -- the shard was cancelled, skipped, or never wrote an
     artifact. Named by index.
  2. a report is DUPLICATED -- two jobs claiming the same (cell, index), which
     means the matrix and the plan disagree about n.
  3. the sum is SHORT -- every shard reported, and together they ran fewer
     tests than the cell collected. This is the one that catches a deselection
     that happened to be spread across shards.
  4. a shard SKIPPED a test nobody declared -- collected, reported, not
     executed. Counted separately from the sum, because junit's ``tests``
     attribute includes skips and comparing that number alone would let 200
     skipped tests pass. Declared skips (scripts/ci_expected_skips.json) are
     tolerated and MUST still close the arithmetic: the gap is allowed exactly
     as far as it is explained.
  5. a shard reported skips it could not NAME, so none of them can be matched
     against the declared list. A count without its observations is half a
     measurement.
  6. the shards of one cell DISAGREE about how many tests that cell collected,
     which makes the denominator a guess.
  7. a skip declared BY CELL did not hold on a cell (added 2026-11-28, lane
     ci-checks28). A skip declared by NAME alone is tolerated on every cell,
     so it passes whether or not the cell meant to RUN the test ran it: the
     tolerance cannot see a lost source. So ``ci_expected_skips.json``'s
     ``by_cell`` rules name, for each test, the operating systems that must
     skip it and the ones that must run it. ``record`` writes each ruled
     test's outcome into the shard's report (``ruled_outcomes``), and every
     cell is held to its system's half of each rule:
       * a system that must SKIP a test must skip it, by name, in exactly
         one shard;
       * a system that must RUN it must report it run -- passed, failed or
         xfailed -- in exactly one shard. A skip there is a failure, and so
         is a test the cell never collected;
       * a system a rule does not name at all is a finding too, so a cell
         added to the matrix cannot arrive unconstrained.
     A run without a cell of some named system cannot check that half, and
     ``verify`` says so by name instead of passing in silence. A rule holds a
     run only when SOME cell reported at least one of its tests: a run in which
     none did is another suite's (this repository's own tests feed ``verify``
     synthetic ones), and ``verify`` says that by name too. Tests that vanish
     from EVERY cell at once are caught where the rule's tests live:
     ``tests/test_a_skip_declared_by_cell_holds_on_every_cell.py`` collects
     them on every cell.

WHY EACH CELL IS SUMMED SEPARATELY rather than everything at once. Collection
is per-checkout-per-platform: a module that fails to import on 3.10 would be
collected on 3.13 and not on 3.10, and one grand total would hide that inside
a bigger number. Comparing a cell's shards against THAT CELL's own collected
count is the only comparison where both sides came from the same machine.

THE EXPECTED CELLS AND SHARD COUNT ARE NOT WRITTEN HERE. They are passed in
from the same workflow output the job matrix is built from, so the guard cannot
expect a shape the matrix does not produce. A hard-coded list here would be a
second source of truth, and the first thing it would do is go stale.

THE RUNNER EACH SHARD RAN ON, ADDED 2026-11-27 (lane ci8). ``record --runner``
takes the file ``scripts/ci_runner_facts.py`` wrote before the run -- the
workers ``-n auto`` started, the CPUs, the free memory -- and carries it into
the report as ``runner``; ``verify`` prints it for every shard. It is evidence
for reading a slow shard, never a condition: a shard whose facts are missing
reports ``runner: null`` and nothing here goes red over it.

USAGE
    python scripts/ci_shard_totals.py record \\
        --plan shard-plan.json --junit junit.xml \\
        --cell '{"os":"ubuntu-latest","python-version":"3.13"}' \\
        --runner runner-facts.json \\
        --out reports/ubuntu-latest-3.13-0.json

    python scripts/ci_shard_totals.py verify \\
        --reports reports/ --of 6 \\
        --cells '[{"os":"ubuntu-latest","python-version":"3.13"}]'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# stdlib ElementTree, on the terms scripts/ci_full_run_check.py argues at
# length: the only document parsed is the junit report pytest wrote seconds
# earlier in this same job.
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# ONE spelling of a runner's line, shared with the step that measured it.
from ci_runner_facts import summary as runner_summary  # noqa: E402


def cell_label(cell: dict) -> str:
    """One spelling of a matrix cell, used by both halves of this file.

    ``record`` labels a report with it and ``verify`` builds its expectations
    with it, from the same function, so the two can never disagree about how
    to write "ubuntu-latest, 3.13" while agreeing about everything else.
    """
    missing = [key for key in ("os", "python-version") if key not in cell]
    if missing:
        raise SystemExit(
            f"FAIL: a matrix cell is missing {missing}; got {sorted(cell)}. "
            f"This label is how a report is matched to the cell that was "
            f"expected to produce it, so a cell that cannot be labelled "
            f"cannot be checked."
        )
    return f"{cell['os']} py{cell['python-version']}"


def junit_totals(path: str) -> dict:
    """Counts from one shard's junit report, with XFAIL SEPARATED FROM SKIP.

    junit uses one <skipped> element for both and tells them apart only by
    ``type``; the ``skipped=`` attribute adds them together. Reading that
    attribute is what made scripts/ci_full_run_check.py refuse a fully green
    run of this suite on 2026-09-05 -- it counted
    tests/test_click_is_not_its_own_evidence.py's deliberate
    ``xfail(strict=True)`` as a test that could not run. An xfail RAN. The
    distinction is kept here for the same reason and, more sharply, because
    this file SUMS across shards: one xfail counted as a skip would make every
    cell short by one and report a completeness gap that does not exist.
    (That test file was deleted on 2026-09-27 with the send_message write it
    tested; the rule stands.)
    """
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise SystemExit(f"FAIL: {path} contains no <testsuite> element")
    totals = {
        key: int(suite.get(key, 0))
        for key in ("tests", "failures", "errors", "skipped")
    }
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
    # Carried into the report so the totals job can NAME the skipped tests
    # across every shard at once. That view exists nowhere else: each shard log
    # holds its own, and a reader hunting four skips across eighteen jobs is
    # doing by hand what one line can do.
    totals["skipped_tests"] = names
    if len(kinds) != int(suite.get("skipped", 0)):
        raise SystemExit(
            f"FAIL: {path} says skipped={suite.get('skipped')} but holds "
            f"{len(kinds)} <skipped> element(s)."
        )
    return totals


def junit_outcomes(path: str, names: set[str]) -> dict[str, str]:
    """The outcome of every NAMED test in one shard's junit report.

    Only the tests a ``by_cell`` rule names are read, so a report stays small:
    the rule needs to know that the Windows cell RAN its tests, not what every
    other test did. An outcome is one word -- ``passed``, ``failed``,
    ``error``, ``xfailed`` or ``skipped`` -- read from the testcase's own
    children, with an error first and the xfail kept apart from the skip, as
    :func:`junit_totals` keeps them.
    """
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise SystemExit(f"FAIL: {path} contains no <testsuite> element")
    outcomes: dict[str, str] = {}
    for case in suite.iter("testcase"):
        name = f"{case.get('classname')}::{case.get('name')}"
        if name not in names:
            continue
        skipped = case.find("skipped")
        if case.find("error") is not None:
            outcome = "error"
        elif case.find("failure") is not None:
            outcome = "failed"
        elif skipped is None:
            outcome = "passed"
        elif skipped.get("type", "") == "pytest.xfail":
            outcome = "xfailed"
        else:
            outcome = "skipped"
        outcomes[name] = outcome
    return outcomes


def publish(line: str) -> None:
    print(line, flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def runner_facts(path: str | None) -> dict | None:
    """The facts ``ci_runner_facts.py`` wrote, or None when there are none.

    Absent is a finding, not a failure: the report step runs ``if: always()``,
    and a shard whose facts step never ran must still report its counts.
    """
    if not path or not Path(path).is_file():
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def record(args) -> int:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    totals = junit_totals(args.junit)
    runner = runner_facts(args.runner)
    ruled = ruled_names(cell_rules())
    report = {
        "cell": cell_label(json.loads(args.cell)),
        "index": plan["index"],
        "of": plan["of"],
        "collected_total": plan["collected_total"],
        "shard_expected": plan["tests"],
        "ran": totals["tests"],
        "skipped": totals["skipped"],
        "skipped_tests": totals["skipped_tests"],
        "xfailed": totals["xfailed"],
        "failures": totals["failures"],
        "errors": totals["errors"],
        "runner": runner,
        # Failure mode 7: the outcome of each test a by-cell rule names, so the
        # totals job can tell a cell that RAN it from one that skipped it or
        # never collected it. Empty when no rule names a test in this shard.
        "ruled_outcomes": junit_outcomes(args.junit, ruled) if ruled else {},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    publish(
        f"shard {report['index']}/{report['of']} on {report['cell']}: "
        f"expected {report['shard_expected']}, ran {report['ran']}, "
        f"skipped {report['skipped']}, xfailed {report['xfailed']}, "
        f"failed {report['failures']}, errors {report['errors']}"
    )
    publish(runner_summary(runner))
    return 0


EXPECTED_SKIPS_PATH = Path(__file__).resolve().parent / "ci_expected_skips.json"


def expected_skips(path: Path = EXPECTED_SKIPS_PATH) -> dict:
    """The declared skips, read from the same file ci_full_run_check.py reads.

    ONE FILE, TWO READERS. The per-shard check and this cross-shard sum have to
    agree about which skips are structural, and the cheapest way for two
    guards to agree is for there to be nothing to disagree about. Absent means
    none, which is the strict original behaviour.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))["expected"]


def cell_rules(path: Path = EXPECTED_SKIPS_PATH) -> list[dict]:
    """The skips declared BY CELL (failure mode 7), from the same file.

    Each rule is ``{"why", "skipped_on_os", "executed_on_os", "tests"}``.
    A rule only NARROWS a declaration and never widens it: every test it names
    must also be declared by name under ``expected``, which is what lets the
    per-shard check tolerate the skip at all. Absent means no rules, so a file
    without the key keeps the name-only behaviour it always had.
    """
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("by_cell", [])


def ruled_names(rules: list[dict]) -> set[str]:
    return {name for rule in rules for name in rule["tests"]}


def active_rules(reports: list[dict], rules: list[dict]) -> list[dict]:
    """The rules this run can hold its cells to: each one at least one of whose tests SOME cell
    reported. A rule none of whose tests any cell reported is a run of another suite, which
    ``verify`` names as not checked."""
    reported = {name for report in reports for name in report.get("ruled_outcomes", {})}
    return [rule for rule in rules if reported & set(rule["tests"])]


def os_of(label: str) -> str:
    """The operating system of a :func:`cell_label`, its one spelling read back."""
    return label.rsplit(" py", 1)[0]


#: Outcomes that mean a test RAN on a cell. An error is not one of them: a test
#: whose setup failed never ran its body.
RAN = frozenset({"passed", "failed", "xfailed"})


def cell_rule_problems(label: str, found: list[dict], rules: list[dict]) -> list[str]:
    """Failure mode 7 for one cell: each rule's half for this cell's system."""
    system = os_of(label)
    problems: list[str] = []
    outcomes: dict[str, list[str]] = {}
    for report in found:
        if "ruled_outcomes" not in report:
            problems.append(
                f"{label}: shard {report.get('index')}'s report carries no ruled "
                f"outcomes, so the by-cell rules cannot be checked against it. "
                f"A rule nobody can check is a name-only declaration again."
            )
            continue
        for name, outcome in report["ruled_outcomes"].items():
            outcomes.setdefault(name, []).append(outcome)
    for rule in rules:
        skip_on, run_on = set(rule["skipped_on_os"]), set(rule["executed_on_os"])
        if system not in skip_on | run_on:
            problems.append(
                f"{label}: a by-cell rule over {len(rule['tests'])} test(s) says "
                f"nothing about {system}, so this cell is unconstrained. Name it "
                f"under skipped_on_os or executed_on_os."
            )
            continue
        for name in rule["tests"]:
            seen = outcomes.get(name, [])
            if len(seen) > 1:
                problems.append(
                    f"{label}: {name} was reported by {len(seen)} shards of this "
                    f"cell, so the shard plan is not a partition here."
                )
                continue
            got = seen[0] if seen else None
            said = "never collected or reported it" if got is None else f"reported it {got}"
            if system in skip_on and got != "skipped":
                problems.append(
                    f"{label}: {name} is declared to SKIP on {system}, by name, "
                    f"and this cell {said}."
                )
            elif system in run_on and got not in RAN:
                problems.append(
                    f"{label}: {name} must RUN on {system}, and this cell {said}. "
                    f"A skip declared by name is tolerated on every cell, so "
                    f"without this rule nothing would have said so."
                )
    return problems


def problems_in(
    reports: list[dict],
    labels: list[str],
    of: int,
    declared: dict | None = None,
    rules: list[dict] | None = None,
) -> list[str]:
    """Every way this set of reports fails to account for the whole suite.

    Returns ALL of them rather than the first. A run where one shard vanished
    AND another ran short is two findings, and stopping at the first would send
    somebody back for a second look after they had fixed one of them.

    ``rules`` are the by-cell rules (failure mode 7); None checks none, which is
    how every caller before them reads.
    """
    declared = {} if declared is None else declared
    rules = active_rules(reports, rules or [])
    problems: list[str] = []
    by_cell: dict[str, list[dict]] = {label: [] for label in labels}

    for report in reports:
        label = report.get("cell")
        if label not in by_cell:
            problems.append(
                f"a report arrived from cell {label!r}, which is not one of "
                f"the {len(labels)} cells the matrix declares ({labels}). "
                f"Either the matrix changed under the guard or an artifact "
                f"from another run leaked in."
            )
            continue
        by_cell[label].append(report)

    for label in labels:
        found = by_cell[label]
        seen: dict[int, int] = {}
        for report in found:
            seen[report["index"]] = seen.get(report["index"], 0) + 1

        missing = sorted(set(range(of)) - set(seen))
        if missing:
            problems.append(
                f"{label}: shard(s) {missing} reported NOTHING. A shard that "
                f"did not report is a shard whose tests nobody ran, and it "
                f"leaves no trace in any other shard's numbers -- which is "
                f"exactly why this is checked against the matrix rather than "
                f"against what turned up."
            )
        duplicated = sorted(index for index, count in seen.items() if count > 1)
        if duplicated:
            problems.append(
                f"{label}: shard index/indices {duplicated} reported more than "
                f"once, so the matrix and the shard plan disagree about how "
                f"many shards exist."
            )
        stray = sorted(index for index in seen if not 0 <= index < of)
        if stray:
            problems.append(
                f"{label}: shard index/indices {stray} are outside 0..{of - 1}."
            )
        if not found:
            continue
        if rules:
            problems.extend(cell_rule_problems(label, found, rules))

        collected = {report["collected_total"] for report in found}
        if len(collected) > 1:
            problems.append(
                f"{label}: shards disagree about how many tests this checkout "
                f"collects ({sorted(collected)}). They ran the same commit on "
                f"the same platform, so they cannot both be right, and summing "
                f"against either number would be summing against a guess."
            )
            continue

        expected = collected.pop()
        skipped = sum(report["skipped"] for report in found)
        executed = sum(report["ran"] for report in found) - skipped
        named = sorted(
            name for report in found for name in report.get("skipped_tests", [])
        )
        unexpected = [name for name in named if name not in declared]
        tolerated = [name for name in named if name in declared]

        # THE GAP IS ALLOWED EXACTLY AS FAR AS IT IS EXPLAINED. Not "skips are
        # fine now" -- the arithmetic still has to close, with every missing
        # test accounted for by a declaration somebody wrote down.
        if executed + len(tolerated) != expected:
            problems.append(
                f"{label}: {expected} tests were collected, {executed} were "
                f"executed across the shards and {len(tolerated)} are declared "
                f"skips -- a gap of {expected - executed - len(tolerated)}."
            )
        if unexpected:
            problems.append(
                f"{label}: {len(unexpected)} test(s) were SKIPPED and not "
                f"declared. A skip is a test that was collected and not "
                f"executed, which is this same defect one layer down; the "
                f"workflow installs what the suite needs in order to skip "
                f"nothing. They were: " + "; ".join(unexpected)
            )
        elif skipped and not named:
            problems.append(
                f"{label}: {skipped} test(s) were SKIPPED and these reports do "
                f"not name them, so none of them can be matched against the "
                f"declared list. A count without its observations is half a "
                f"measurement."
            )

    return problems


def verify(args) -> int:
    directory = Path(args.reports)
    if not directory.is_dir():
        raise SystemExit(f"FAIL: {directory} is not a directory")
    files = sorted(directory.rglob("*.json"))
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    labels = [cell_label(cell) for cell in json.loads(args.cells)]
    if len(set(labels)) != len(labels):
        raise SystemExit(f"FAIL: the declared cells are not distinct: {labels}")

    declared = expected_skips()
    rules = cell_rules()
    publish(
        f"shard reports: {len(reports)} found, "
        f"{len(labels)} cell(s) x {args.of} shard(s) expected, "
        f"{len(declared)} declared skip(s), {len(rules)} by-cell rule(s)"
    )
    # WHAT THIS RUN CANNOT CHECK, said by name. The lane fast path has no
    # Windows cell, so a rule's Windows half is checked only by the full matrix.
    systems = {os_of(label) for label in labels}
    live = active_rules(reports, rules)
    for rule in rules:
        if rule not in live:
            publish(
                f"  NOT CHECKED in this run: a by-cell rule over {len(rule['tests'])} "
                f"test(s) -- no cell reported any of them"
            )
            continue
        for half, named in (("skip", rule["skipped_on_os"]), ("run", rule["executed_on_os"])):
            for system in sorted(set(named) - systems):
                publish(
                    f"  NOT CHECKED in this run: the rule that {len(rule['tests'])} "
                    f"test(s) {half} on {system} -- no {system} cell in this run"
                )
    for label in labels:
        found = [report for report in reports if report.get("cell") == label]
        if found:
            collected = found[0]["collected_total"]
            skipped = sum(report["skipped"] for report in found)
            executed = sum(report["ran"] for report in found) - skipped
            publish(
                f"  {label}: collected {collected} | executed {executed} | "
                f"skipped {skipped} | shards {sorted(r['index'] for r in found)}"
            )
            # Every shard's runner, side by side: a slow shard is read against
            # its siblings' workers, CPUs and free memory, not in isolation.
            for report in sorted(found, key=lambda r: r["index"]):
                publish(f"    {label} shard {report['index']} "
                        f"{runner_summary(report.get('runner'))}")
        else:
            publish(f"  {label}: NO REPORTS")

    problems = problems_in(reports, labels, args.of, declared, rules)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print(
        f"OK: every one of {len(labels)} cell(s) ran all {args.of} shards, and "
        f"their executed tests add up to what that cell collected"
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    writer = sub.add_parser("record", help="write one shard's report")
    writer.add_argument("--plan", required=True, help="ci_shard.py --json output")
    writer.add_argument("--junit", required=True, help="this shard's junit.xml")
    writer.add_argument("--cell", required=True, help="the matrix cell, as JSON")
    writer.add_argument("--runner", help="ci_runner_facts.py's file; absent is recorded as null")
    writer.add_argument("--out", required=True, help="where to write the report")
    writer.set_defaults(run=record)

    checker = sub.add_parser("verify", help="add every shard's report up")
    checker.add_argument("--reports", required=True, help="directory of reports")
    checker.add_argument("--of", type=int, required=True, help="shards per cell")
    checker.add_argument("--cells", required=True, help="the matrix cells, JSON")
    checker.set_defaults(run=verify)

    args = parser.parse_args(argv[1:])
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
