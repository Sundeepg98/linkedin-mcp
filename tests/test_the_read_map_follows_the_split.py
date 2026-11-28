"""The impact gate's observed read map knows the files ``tests/test_writes.py``
was split into.

WHY. ``scripts/impact_gate_read_map.json`` records which test file was seen
reading which data file, and the gate adds those readers to a scoped plan.
On 2026-11-27 lane ci8 split ``tests/test_writes.py`` into six files, and the
map, a recording of 2026-09-22, still attributed every fixture those tests
read to ``tests/test_writes.py`` alone. Measured before the re-record, through
the shipped ``impact_gate.impact_set``: an edit to
``tests/fixtures/manage_pages_following_hydrated.html`` selected one of the
six files, and not ``tests/test_writes_list.py``, where the unfollow tests that
read it now live; an edit to ``tests/fixtures/jobs_tracker_empty.html``
selected one of the six, and not ``tests/test_writes_state.py``. The gate
under-selected in silence, because the map may only ADD to a plan and a file
missing from it looks like a file with no reads.

WHAT IS PINNED. Each pair below is a fixture and a split file whose tests read
it at run time, taken from the test code (the line that reads it is named),
and the map must name that file for that fixture. Through the gate's union
rule (``impact_gate.observed_readers`` feeds ``impact_set``, and an observed
reader is always added), a file named here is in the plan for that edit.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import impact_gate as G  # noqa: E402

#: (fixture, split file, the code in that file that reads it at run time)
SPLIT_READERS = [
    ("tests/fixtures/manage_pages_following_hydrated.html", "tests/test_writes_list.py",
     "every unfollow test serves _manage_pages(), which reads the capture"),
    ("tests/fixtures/jobs_tracker_empty.html", "tests/test_writes_state.py",
     "test_the_saved_gate_renders_on_the_list_he_actually_has serves the empty tracker"),
    ("tests/fixtures/job_detail.html", "tests/test_writes_perform.py",
     "the save runs end to end over the posting capture"),
    ("tests/fixtures/job_detail.html", "tests/test_writes_gate.py",
     "the gate renders the posting it read"),
]


#: AND READERS THE 2026-09-22 RECORDING NEVER SAW (lane ci8, 2026-11-28),
#: found once the full recording ran on CI (run 46067022556). Each reads the
#: fixture through a name no static rule can match, and the stale map left it
#: out of the plan for an edit to that fixture: measured through the shipped
#: ``impact_set``, red against the old map and green against the new one.
STALE_MAP_MISSED = [
    ("tests/fixtures/synthetic/messaging_compose_list.html", "tests/test_people_seam.py",
     "it imports COMPOSE_LIST, the fixture's text, from tests/test_messaging_threads.py"),
]


@pytest.mark.parametrize(("fixture", "reader", "why"), SPLIT_READERS + STALE_MAP_MISSED,
                         ids=[f"{r.split('/')[-1]}<-{f.split('/')[-1]}"
                              for f, r, _w in SPLIT_READERS + STALE_MAP_MISSED])
def test_the_map_names_the_split_file_that_reads_the_fixture(fixture, reader, why):
    assert (_ROOT / fixture).is_file() and (_ROOT / reader).is_file(), (fixture, reader)
    seen, stamp = G.observed_readers([fixture])
    assert stamp is not None, "there is no observed read map on disk"
    assert reader in seen, (
        f"the read map does not name {reader} as a reader of {fixture} ({why}), "
        f"so a scoped gate run for an edit to it leaves those tests out. It "
        f"names {sorted(seen)}. Re-record the file with scripts/build_read_map.py."
    )
