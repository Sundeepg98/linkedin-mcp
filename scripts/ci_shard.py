#!/usr/bin/env python3
"""Split this suite's test FILES into N shards of roughly equal cost.

WHY THIS FILE EXISTS. The suite runs 3660 tests in 27m16s serially, on one
machine, and CI ran it that way in every matrix cell. The repository is public,
so GitHub Actions minutes are free (measured with ``gh repo view``:
isPrivate=false) and the cost of a slow gate is WALL CLOCK, which more runners
buy back. Sharding at FILE granularity across jobs needs no new dependency:
pytest already accepts a list of files, and every test in this suite belongs to
exactly one file.

THE ONE PROPERTY THIS MUST HAVE. A sharded suite that drops a shard goes GREEN
HAVING RUN LESS, which is worse than no gate at all. So the split is a
PARTITION -- every collected file in exactly one shard, no file in two, none in
none -- and that is asserted in tests/test_ci_shard.py rather than asserted
here in prose. The cross-job half of the same guard, which is the half that
catches a shard that never reported, lives in scripts/ci_shard_totals.py.

BALANCE BY COST, NOT BY FILE COUNT. Round-robin over 92 names gives one shard
holding tests/test_no_committed_identity.py (279 tests) and another holding
tests/test_result_verification_block.py (2), and the gate is still as slow as
the worst shard. The packing is greedy longest-processing-time-first: sort
heaviest first, and put each file in the lightest shard so far. LPT is not
optimal -- optimal bin-packing is NP-hard and worth nothing here -- but it is
within 4/3 of optimal by a classical bound, it is one sort plus one pass, and
it is deterministic.

AND THE WEIGHT IS SECONDS, NOT TESTS, WHICH IS THE OPPOSITE OF WHAT THIS FILE
FIRST DID. Test count was the obvious weight and it packs beautifully -- at
n=6 the shards come out 613/610/609/608/608/612 tests, a spread of five. Then
the same split was priced against a full serial run's junit report and the
same six shards read:

    244s  177s  207s  272s  575s  172s        <- weighted by TEST COUNT

because the per-test cost in this suite spans 0.005s to 14.9s, a factor of
2900. tests/test_verification_that_could_not_read.py is 5 tests and 74s;
tests/test_no_committed_identity.py is 279 tests and under 4s. A gate is as
slow as its slowest shard, so counting tests bought a 575s gate where 275s was
available -- and it LOOKED perfectly balanced the whole time, which is the
part worth remembering.

Weighted by SECONDS the same 92 files land within a tenth of a second of the
arithmetic ideal, because LPT places the tiny files last and they level the
bins to within the smallest of them:

    n=4   411.889s .. 411.914s     spread 0.025s   (ideal 411.901s)
    n=6   274.578s .. 274.639s     spread 0.061s   (ideal 274.601s)
    n=8   205.898s .. 205.998s     spread 0.100s   (ideal 205.951s)
    n=9   183.027s .. 183.097s     spread 0.070s   (ideal 183.067s)
    n=12  133.340s .. 180.569s     spread 47.2s    (ideal 137.300s)

Measured 2026-09-05 at e0dc8f9, 3660 tests, 1647.6s of test time. n=12 is in
that table to show where the method STOPS working: the floor for any
file-level split is the biggest single FILE, and
tests/test_save_candidates_fixture.py is 180.6s on its own, so past nine
shards the extra runners wait on one file no matter how the weights are
computed.

WHERE THE SECONDS COME FROM, AND WHY THAT IS SAFE. Collection is live;
scripts/ci_shard_timings.json is a committed measurement. The two do different
jobs and only one of them can hurt:

  * MEMBERSHIP comes from ``pytest --collect-only -q`` in the checkout being
    sharded, every time. A file added today is sharded today.
  * WEIGHT comes from the timings file, and a file it has never heard of is
    priced at the measured mean seconds-per-test. So a stale table can only
    UNBALANCE a shard. It cannot lose a test, and there is no arrangement of
    its contents that would.

Regenerate it after a change that moves the suite's shape:

    python -m pytest -q --junitxml=junit.xml
    python scripts/ci_shard.py --write-timings junit.xml \\
        --label "e0dc8f9, 2026-09-05, one Windows laptop, serial, cold" \\
        > scripts/ci_shard_timings.json

USAGE
    python scripts/ci_shard.py --index 0 --of 6            # file list, stdout
    python scripts/ci_shard.py --index 0 --of 6 --json     # + counts, for CI
    python scripts/ci_shard.py --of 6 --plan               # every shard, table
    python scripts/ci_shard.py --of 6 --plan --seconds junit.xml   # priced

    # In CI, where collection has already been run and written to a file, pass
    # it in rather than paying for a second collection:
    python -m pytest --collect-only -q > collected.txt
    python scripts/ci_shard.py --index 0 --of 6 --collected collected.txt

With no --collected, this runs ``pytest --collect-only -q`` itself. That
happens inside main() and never at import: importing this module does nothing,
which tests/test_scripts_are_import_safe.py enforces for every script here.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

# stdlib ElementTree on the same terms scripts/ci_full_run_check.py sets out at
# length: the only document parsed here is a junit report pytest wrote, passed
# by hand, to print a prediction that nothing depends on. If this is ever
# pointed at a report from somewhere else, that trade changes and so should
# this line.
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TIMINGS = Path(__file__).resolve().parent / "ci_shard_timings.json"

#: pytest ends ``--collect-only -q`` with "3660 tests collected in 6.19s", or
#: with "3 tests collected, 4 errors" when collection itself broke. Both forms
#: are parsed, because the second one has to be REFUSED rather than silently
#: sharded -- a checkout whose collection errored knows about fewer files than
#: it contains, and sharding that list would drop every test in the broken
#: module without any shard reporting a gap.
_SUMMARY = re.compile(r"(\d+)\s+tests?\s+collected(?:,\s*(\d+)\s+errors?)?")


def parse_collected(text: str) -> dict[str, int]:
    """Test counts per file, from the stdout of ``pytest --collect-only -q``.

    Node ids are split on the FIRST ``::`` rather than matched with a regex
    over the whole line. A parametrised id carries the parameter in brackets at
    the end -- ``test_x[tests/fixtures/a.html]`` -- and parameters in this suite
    contain paths, spaces and colons, so anything that reads the tail is
    guessing. The head is a file path and nothing else.

    THE PARSE CHECKS ITSELF. pytest prints how many tests it collected; if the
    lines this function accepted do not add up to that number, the parse is
    wrong and the caller is told so instead of being handed a short list. That
    control matters more than it looks: every way this function could quietly
    under-read -- an id shape it does not recognise, output truncated by a pipe,
    a warnings block that swallowed lines -- produces a shard plan that is a
    valid partition of the WRONG SET, and a partition test cannot see it.
    """
    counts: dict[str, int] = {}
    seen = 0
    for raw in text.splitlines():
        line = raw.strip()
        if "::" not in line:
            continue
        head = line.split("::", 1)[0]
        if not head.endswith(".py") or " " in head:
            continue
        counts[head] = counts.get(head, 0) + 1
        seen += 1

    summary = _SUMMARY.findall(text)
    if not summary:
        raise SystemExit(
            "FAIL: the collection output holds no 'N tests collected' line, so "
            "how many tests this checkout contains is unknown. Collection "
            "itself probably failed; its tail follows.\n\n" + text[-4000:]
        )
    # Last match: a rerun, or a warnings block, can put earlier numbers above.
    declared, errors = summary[-1]
    if errors and int(errors):
        raise SystemExit(
            f"FAIL: collection reported {errors} error(s). The file list is "
            f"short by whatever the broken module holds, and sharding a short "
            f"list loses those tests in a way no shard can report."
        )
    if int(declared) != seen:
        raise SystemExit(
            f"FAIL: collection says {declared} tests, this parse found {seen}. "
            f"Sharding a list that does not reconcile would produce a tidy "
            f"partition of the wrong set."
        )
    return counts


def load_timings(path: Path = TIMINGS) -> dict[str, float]:
    """The committed per-file seconds, or an empty mapping if there are none.

    A MISSING FILE IS NOT AN ERROR. Sharding by test count is worse balance,
    not a broken gate, and a splitter that refuses to run because a measurement
    is absent would take CI down over a tuning parameter.
    """
    if not path.exists():
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    return {name: float(value) for name, value in document["seconds"].items()}


def pack_weights(counts: dict[str, int], timings: dict[str, float]) -> dict[str, float]:
    """Cost per file: measured seconds where known, estimated where not.

    THE KEY SET IS ``counts``, ALWAYS, and that is the whole safety argument
    for using a committed measurement at all. Files the timings have never
    heard of keep their place; files the timings still remember but collection
    no longer reports are dropped. So the timings can be arbitrarily stale and
    the split is still a partition of what exists -- only its BALANCE decays.

    An unpriced file is estimated at the measured MEAN seconds-per-test, not
    the median. The median in this suite is 0.10 s/test and the mean is 0.45,
    because most files are cheap and a few are enormous; a new file is as
    likely to be a browser module as a static guard, and under-pricing one of
    those is the mistake that lands two 180s files in the same shard.
    """
    if not timings:
        return {name: float(count) for name, count in counts.items()}

    priced = [name for name in counts if name in timings]
    seconds = sum(timings[name] for name in priced)
    tests = sum(counts[name] for name in priced)
    rate = (seconds / tests) if tests else 1.0
    return {
        name: timings.get(name, count * rate) for name, count in counts.items()
    }


def plan_shards(weights: dict[str, float], of: int) -> list[list[str]]:
    """Pack files into ``of`` shards, heaviest first into the lightest shard.

    Deterministic on two counts, and both are load-bearing for a gate that must
    mean the same thing on a Windows runner and an ubuntu one:

    * the pack order is ``(-weight, path)``, so files of equal weight break
      their tie on the path rather than on whatever order the parse or the
      filesystem produced;
    * a tie between two equally-loaded shards goes to the LOWER INDEX, never to
      ``min``'s first-seen-wins over an unordered structure.

    Each returned shard is sorted by path, so a diff between two runs of this
    script is empty or meaningful, never a reordering.
    """
    if of < 1:
        raise SystemExit(f"FAIL: --of must be at least 1, got {of}")

    files = sorted(weights)
    if of > len(files):
        raise SystemExit(
            f"FAIL: asked for {of} shards over {len(files)} test files. Some "
            f"shard would be empty, and an empty file list handed to pytest "
            f"runs the WHOLE SUITE rather than nothing -- so this is refused "
            f"here instead of being discovered as a shard that mysteriously "
            f"took 27 minutes."
        )

    shards: list[list[str]] = [[] for _ in range(of)]
    loads = [0] * of
    for path in sorted(files, key=lambda name: (-weights[name], name)):
        target = min(range(of), key=lambda index: (loads[index], index))
        shards[target].append(path)
        loads[target] += weights[path]
    return [sorted(shard) for shard in shards]


def seconds_per_file(junit_path: str, known: dict[str, int]) -> dict[str, float]:
    """Per-file seconds from a junit report, for --plan's prediction column.

    Only used to PRINT a prediction. Nothing in the split depends on it, which
    is why a junit report from an older commit is safe to pass here.

    pytest's xunit2 report carries NO path -- measured, after this function was
    first written to read a ``file`` attribute and silently returned an empty
    mapping, which --plan rendered as a missing column rather than as an error.
    What it carries is ``classname``, the dotted module ("tests.test_auth", or
    "tests.test_auth.TestLogin" for a test in a class). So the dotted name is
    resolved against the files collection actually reported, longest prefix
    first, and a classname that matches nothing is DROPPED rather than turned
    into a path by string surgery: the alternative is a prediction with an
    invented row in it.
    """
    root = ET.parse(junit_path).getroot()
    totals: dict[str, float] = {}
    for case in root.iter("testcase"):
        parts = (case.get("classname") or "").split(".")
        while parts:
            candidate = "/".join(parts) + ".py"
            if candidate in known:
                totals[candidate] = totals.get(candidate, 0.0) + float(
                    case.get("time", 0.0)
                )
                break
            parts.pop()
    return totals


def _no_timings_message(junit_path: str, counts: dict[str, int]) -> str:
    return (
        f"FAIL: {junit_path} produced timings for none of the {len(counts)} "
        f"collected files. A junit report from another repository would do "
        f"that, and so would a report shape this parse does not read -- either "
        f"way the result would otherwise be an empty column rather than a "
        f"problem, which is how the first version of this went unnoticed."
    )


def _collect_via_pytest() -> str:
    """Run collection in this checkout. Called from main(), never on import."""
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return done.stdout + done.stderr


def main(argv: list[str]) -> int:
    # LF, on Windows too. The workflow reads this list back with
    # ``$(cat shard-files.txt)`` in Git Bash, and word splitting happens on
    # IFS -- space, tab, newline -- which does not include the carriage return
    # that Python's text mode would add on the Windows cell. Every path would
    # then arrive at pytest with a trailing \r and be reported as not existing,
    # on one third of the matrix and nowhere else.
    sys.stdout.reconfigure(newline="\n")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--index", type=int, help="which shard, 0-based")
    parser.add_argument("--of", type=int, help="how many shards")
    parser.add_argument(
        "--collected",
        help="stdout of `pytest --collect-only -q`; collected live if omitted",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit the shard as a JSON object"
    )
    parser.add_argument(
        "--plan", action="store_true", help="print every shard and its weight"
    )
    parser.add_argument(
        "--seconds",
        help="a junit.xml, to price --plan's shards against a real run",
    )
    parser.add_argument(
        "--write-timings",
        metavar="JUNIT",
        help="emit a new ci_shard_timings.json from this junit report",
    )
    parser.add_argument(
        "--label", help="provenance line for --write-timings; required with it"
    )
    args = parser.parse_args(argv[1:])

    if args.collected:
        text = Path(args.collected).read_text(encoding="utf-8", errors="replace")
    else:
        text = _collect_via_pytest()
    counts = parse_collected(text)
    total = sum(counts.values())

    if args.write_timings:
        # A measurement ships with the provenance of the run it came from, or
        # it does not ship: a table of seconds with no commit, machine or date
        # against it cannot be judged stale by anybody who finds it later.
        if not args.label:
            parser.error("--write-timings needs --label naming the run it came from")
        measured = seconds_per_file(args.write_timings, counts)
        if not measured:
            raise SystemExit(_no_timings_message(args.write_timings, counts))
        print(
            json.dumps(
                {
                    "_measured": args.label,
                    "_files": len(measured),
                    "_tests": total,
                    "_total_seconds": round(sum(measured.values()), 1),
                    "seconds": {name: round(value, 3) for name, value in sorted(measured.items())},
                },
                indent=2,
            )
        )
        return 0

    if args.of is None:
        parser.error("--of is required unless --write-timings is given")
    weights = pack_weights(counts, load_timings())
    shards = plan_shards(weights, args.of)

    if args.plan:
        measured = seconds_per_file(args.seconds, counts) if args.seconds else {}
        if args.seconds and not measured:
            raise SystemExit(_no_timings_message(args.seconds, counts))
        for index, shard in enumerate(shards):
            tests = sum(counts[path] for path in shard)
            cost = sum(weights[path] for path in shard)
            line = (
                f"shard {index}/{args.of}: {len(shard):3d} files, "
                f"{tests:5d} tests, {cost:8.1f} weight"
            )
            if measured:
                line += f", {sum(measured.get(p, 0.0) for p in shard):8.1f}s measured"
            print(line)
        if measured:
            print(f"timings cover {len(measured)} of {len(counts)} files")
        print(f"total: {len(counts)} files, {total} tests")
        return 0

    if args.index is None:
        parser.error("--index is required unless --plan is given")
    if not 0 <= args.index < args.of:
        parser.error(f"--index must be in 0..{args.of - 1}, got {args.index}")

    shard = shards[args.index]
    if args.json:
        print(
            json.dumps(
                {
                    "index": args.index,
                    "of": args.of,
                    "files": shard,
                    # COUNTS, never the packing weight. This number is what
                    # the totals guard compares a junit report against, and a
                    # junit report counts tests, not seconds.
                    "tests": sum(counts[path] for path in shard),
                    "collected_total": total,
                    "files_total": len(counts),
                },
                indent=2,
            )
        )
    else:
        for path in shard:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
