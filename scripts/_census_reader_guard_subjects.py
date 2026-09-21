"""Live census of the reader-leak guard's discovered subject set.

Imports ``discover_readers`` from ``tests.test_readers_emit_no_page_string``
(the shipped instrument -- not reimplemented) and compares what it finds
TODAY, at HEAD, against the committed baseline's key set.

Read-only: does not drive any reader, does not touch the baseline file
except to read it, does not open a browser. Prints ASCII-only, no absolute
filesystem paths -- module:function names only.

Run from the repo root:
    venv/Scripts/python scripts/_census_reader_guard_subjects.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_readers_emit_no_page_string import discover_readers  # noqa: E402

BASELINE_PATH = REPO_ROOT / "tests" / "reader_leak_baseline.json"


def main() -> None:
    live_pairs = discover_readers()
    live_names = [name for name, _fn in live_pairs]
    live_set = set(live_names)

    print(f"LIVE DISCOVERY COUNT (discover_readers() at HEAD): {len(live_names)}")

    # sanity: discover_readers() promises a sorted, de-duplicated list keyed
    # module:function -- confirm both properties rather than assume them.
    is_sorted = live_names == sorted(live_names)
    is_unique = len(live_names) == len(live_set)
    print(f"  sorted: {is_sorted}")
    print(f"  unique keys: {is_unique}")
    print()

    if not BASELINE_PATH.exists():
        print("BASELINE FILE: MISSING -- cannot compare")
        return

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["readers"]
    baseline_set = set(baseline.keys())

    print(f"BASELINE KEY COUNT: {len(baseline_set)}")
    print()

    equal = live_set == baseline_set
    print(f"LIVE SET EQUALS BASELINE KEY SET: {equal}")

    appeared = sorted(live_set - baseline_set)   # live but not in baseline
    vanished = sorted(baseline_set - live_set)   # in baseline but not live
    sym_diff_size = len(appeared) + len(vanished)

    print(f"SYMMETRIC DIFFERENCE SIZE: {sym_diff_size}")
    if appeared:
        print(f"  IN LIVE, NOT IN BASELINE ({len(appeared)}):")
        for name in appeared:
            print(f"    + {name}")
    if vanished:
        print(f"  IN BASELINE, NOT IN LIVE ({len(vanished)}):")
        for name in vanished:
            print(f"    - {name}")
    if not appeared and not vanished:
        print("  (empty -- the two key sets are identical)")


if __name__ == "__main__":
    main()
