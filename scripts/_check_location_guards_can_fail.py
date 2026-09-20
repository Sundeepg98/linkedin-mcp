"""Prove the multi-location guards BITE. Run, do not trust.

WHY THIS EXISTS, and it is not ceremony. Census row ``J 151`` -- filter a job
search by MULTIPLE simultaneous locations -- shipped 2026-09-20 as a fan-out:
one ``/jobs/search/`` load per place, merged. The capability is only SAFE
because two url spellings stay unreachable, and both of them were measured
live on 2026-09-05 rather than reasoned about:

    location=A%2C%20B      KEPT by LinkedIn, and returns seven postings of
                           which ZERO are A-only and ZERO are B-only -- it
                           geocodes somewhere neither search reaches.
    location=A&location=B  STRIPPED. LinkedIn serves the LAST city alone.

A guard against a SILENT failure cannot be checked by running it. It is green
when the code is right and green when the guard is dead, and those two look
identical from outside. So this plants fourteen mutations one at a time, runs
the single test node that should catch each one, and restores the file
immediately afterwards.

**IT HAS ALREADY EARNED ITS PLACE.** Its first run, against the guards as
committed in ``576f5e6``, found TWO that could not fail:

  * ``test_the_ceiling_refuses_one_more_than_it_accepts`` built BOTH its inputs
    out of ``jobfilter.MAX_LOCATIONS``, so raising the constant from 5 to 500
    raised the test's own inputs with it and the cap refused nothing while the
    assertion stayed green. A check whose input is derived from the value under
    test measures the derivation, never the value.
  * ``test_the_multi_location_chain_is_still_whole`` matched its function names
    as SUBSTRINGS, so renaming ``merge_location_reads`` to
    ``merge_location_reads_renamed`` left ``"def merge_location_reads"`` in the
    source -- the old name is a prefix of the new one -- and the chain read
    whole while ``server.py``'s call site pointed at nothing.

Neither would have been found by running the suite, because a check that cannot
fail passes. Both were fixed in ``cf76e17`` and this run is now 14 of 14.

EVERY MUTATION IS APPLIED TO A COMMITTED FILE and restored with
``git checkout --`` in a ``finally``, so an interrupt loses nothing. The
restoration is asserted before the summary prints.

Run it from anywhere:  python scripts/_check_location_guards_can_fail.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PYTHON = sys.executable

SERVER = "linkedin_server/server.py"
FILTER = "linkedin_server/jobfilter.py"
CENSUS = "_audit/_census/jobs.md"
FANOUT_TESTS = "tests/test_job_search_multiple_locations.py"
CHAIN_TESTS = "tests/test_a_covered_row_names_the_artifact_that_covers_it.py"
PIN_TESTS = "tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py"
URL_RULING = "tests/test_the_source_url_split_was_never_ruled.py"

#: ``(label, file, find, replace, test node)``. The FIND text must occur
#: EXACTLY ONCE -- a mutation that cannot be placed is reported as
#: ANCHOR-MISS rather than silently skipped, because a battery that quietly
#: plants nothing is the same disease as a guard that cannot fail.
CASES: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "naive fan-out: comma-join the places into ONE url",
        SERVER,
        '        reads: list[tuple[str, dict[str, Any]]] = []\n'
        '        for place in places:',
        '        if plan["state"] == "fanout":\n'
        '            places = [", ".join(places)]\n'
        '        reads: list[tuple[str, dict[str, Any]]] = []\n'
        '        for place in places:',
        FANOUT_TESTS
        + "::test_a_fan_out_builds_one_url_per_place_and_never_joins_them",
    ),
    (
        "naive fan-out: append the location key once per place",
        SERVER,
        '            head: list[tuple[str, str]] = [("keywords", keywords.strip())]\n'
        '            if place.strip():\n'
        '                head.append(("location", place.strip()))',
        '            head: list[tuple[str, str]] = [("keywords", keywords.strip())]\n'
        '            if place.strip():\n'
        '                head.append(("location", place.strip()))\n'
        '                head.append(("location", place.strip()))',
        FANOUT_TESTS
        + "::test_a_fan_out_builds_one_url_per_place_and_never_joins_them",
    ),
    (
        "merge by concatenation instead of round-robin",
        FILTER,
        "    merged: list[dict[str, Any]] = []\n"
        "    for index in range(max((len(rows) for rows in per_place), default=0)):\n"
        "        for rows in per_place:\n"
        "            if index < len(rows):\n"
        "                merged.append(rows[index])",
        "    merged: list[dict[str, Any]] = []\n"
        "    for rows in per_place:\n"
        "        merged.extend(rows)",
        FANOUT_TESTS + "::test_the_merge_is_round_robin_so_a_trim_falls_evenly",
    ),
    (
        "stop de-duplicating by job_id",
        FILTER,
        "            if job_id:\n"
        "                if job_id in seen:\n"
        "                    repeats += 1\n"
        "                    continue\n"
        "                seen.add(job_id)",
        "            if job_id:\n                seen.add(job_id)",
        FANOUT_TESTS + "::test_a_posting_answering_two_places_is_returned_once",
    ),
    (
        "decide the plan AFTER the first page load",
        SERVER,
        '        plan = jobfilter.locations_plan(location, locations)\n'
        '        if plan["state"] == "refused":\n'
        '            return {"error": "bad_argument", "message": plan["why"]}\n'
        '        places: list[str] = plan["places"]',
        '        plan = jobfilter.locations_plan(location, locations)\n'
        '        places: list[str] = plan["places"] or [""]\n'
        '        _refused_later = plan["state"] == "refused"',
        FANOUT_TESTS + "::test_a_refused_plan_loads_no_page_at_all",
    ),
    (
        "let a single entry through instead of refusing the comma trap",
        FILTER,
        "    if len(places) == 1:",
        "    if False:",
        FANOUT_TESTS + "::test_one_place_in_the_plural_argument_is_refused",
    ),
    (
        "quote the caller's place in the refusal",
        FILTER,
        '                "locations named ONE place, and locations means several. The "',
        '                f"locations named ONE place ({places[0]}). The "',
        FANOUT_TESTS + "::test_the_refusal_never_quotes_the_place_the_caller_typed",
    ),
    (
        "raise the ceiling so it refuses nothing",
        FILTER,
        "MAX_LOCATIONS = 5",
        "MAX_LOCATIONS = 500",
        FANOUT_TESTS + "::test_the_ceiling_refuses_one_more_than_it_accepts",
    ),
    (
        "a SECOND url builder appears beside the funnel",
        SERVER,
        "        def _search_url(place: str) -> str:",
        "        def _search_url(place: str) -> str:  # noqa\n"
        "            pass\n\n"
        "        def _search_url(place: str) -> str:",
        CHAIN_TESTS + "::test_the_multi_location_chain_is_still_whole",
    ),
    (
        "the merge helper is RENAMED out from under its call site",
        FILTER,
        "def merge_location_reads(",
        "def merge_location_reads_renamed(",
        CHAIN_TESTS + "::test_the_multi_location_chain_is_still_whole",
    ),
    (
        "the banked row silently reverts to GAP",
        CENSUS,
        "| 151 | Filter a job search by MULTIPLE simultaneous locations "
        "| a523131 | COVERED-UNFIRED |",
        "| 151 | Filter a job search by MULTIPLE simultaneous locations "
        "| a523131 | GAP |",
        CHAIN_TESTS + "::test_the_row_still_claims_the_coverage_it_was_banked_with",
    ),
    (
        "the parameter pin is left at 61",
        PIN_TESTS,
        "PINNED_PARAMETER_COUNT = 62",
        "PINNED_PARAMETER_COUNT = 61",
        PIN_TESTS + "::test_the_pin_itself_is_not_empty",
    ),
    (
        "the source_url ruling is withdrawn",
        URL_RULING,
        '    ("jobfilter.py", "merge_location_reads"): (PASSTHROUGH, 2),',
        "",
        URL_RULING + "::test_every_emission_point_is_declared",
    ),
    (
        "the ruling names ONE site where there are two",
        URL_RULING,
        '    ("jobfilter.py", "merge_location_reads"): (PASSTHROUGH, 2),',
        '    ("jobfilter.py", "merge_location_reads"): (PASSTHROUGH, 1),',
        URL_RULING + "::test_every_emission_point_is_declared",
    ),
)


def _restore(relative: str) -> None:
    subprocess.run(
        ["git", "checkout", "--", relative], cwd=str(ROOT), check=True
    )


def _run_one(label, relative, find, replace, node):
    target = ROOT / relative
    text = target.read_text(encoding="utf-8")
    occurrences = text.count(find)
    if occurrences != 1:
        return label, "ANCHOR-MISS (%d occurrences, wanted 1)" % occurrences
    try:
        target.write_text(text.replace(find, replace), encoding="utf-8")
        proc = subprocess.run(
            [PYTHON, "-m", "pytest", node, "-q", "--no-header", "-x"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
    finally:
        _restore(relative)
    caught = proc.returncode != 0
    return label, "RED (caught)" if caught else "GREEN -- GUARD DID NOT FIRE"


def main() -> int:
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    ).stdout.strip()
    if dirty:
        print(
            "REFUSING TO RUN: the tree has uncommitted changes, and every\n"
            "mutation below is undone with `git checkout --`. Running now\n"
            "would DESTROY that work. Commit first.\n\n" + dirty
        )
        return 2

    results = [_run_one(*case) for case in CASES]

    print()
    print("MUTATION".ljust(62) + "VERDICT")
    print("-" * 92)
    for label, verdict in results:
        print(label.ljust(62) + verdict)

    still_dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    ).stdout.strip()
    print()
    if still_dirty:
        print("RESTORATION FAILED -- the tree is not clean:\n" + still_dirty)
        return 2

    missed = [r for r in results if not r[1].startswith("RED")]
    print("caught %d of %d; tree restored clean" % (len(results) - len(missed),
                                                    len(results)))
    if missed:
        print()
        print("THESE GUARDS DID NOT FIRE. A check that cannot fail certifies")
        print("nothing, and this is the only channel that can say so:")
        for label, verdict in missed:
            print("  - %s -> %s" % (label, verdict))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
