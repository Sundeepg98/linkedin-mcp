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

WHY EACH CELL IS SUMMED SEPARATELY rather than everything at once. Collection
is per-checkout-per-platform: a module that fails to import on 3.10 would be
collected on 3.13 and not on 3.10, and one grand total would hide that inside
a bigger number. Comparing a cell's shards against THAT CELL's own collected
count is the only comparison where both sides came from the same machine.

THE EXPECTED CELLS AND SHARD COUNT ARE NOT WRITTEN HERE. They are passed in
from the same workflow output the job matrix is built from, so the guard cannot
expect a shape the matrix does not produce. A hard-coded list here would be a
second source of truth, and the first thing it would do is go stale.

USAGE
    python scripts/ci_shard_totals.py record \\
        --plan shard-plan.json --junit junit.xml \\
        --cell '{"os":"ubuntu-latest","python-version":"3.13"}' \\
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


def publish(line: str) -> None:
    print(line, flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def record(args) -> int:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    totals = junit_totals(args.junit)
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


def problems_in(
    reports: list[dict],
    labels: list[str],
    of: int,
    declared: dict | None = None,
) -> list[str]:
    """Every way this set of reports fails to account for the whole suite.

    Returns ALL of them rather than the first. A run where one shard vanished
    AND another ran short is two findings, and stopping at the first would send
    somebody back for a second look after they had fixed one of them.
    """
    declared = {} if declared is None else declared
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
    publish(
        f"shard reports: {len(reports)} found, "
        f"{len(labels)} cell(s) x {args.of} shard(s) expected, "
        f"{len(declared)} declared skip(s)"
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
        else:
            publish(f"  {label}: NO REPORTS")

    problems = problems_in(reports, labels, args.of, declared)
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
