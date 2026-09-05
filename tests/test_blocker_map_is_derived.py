"""The blocker map must stay DERIVED, and the UNASSIGNED count must only shrink.

WHY THIS TEST EXISTS. `_audit/2026-09-03-linkedin-gap-blockers.md` divided 409
census GAP rows across 97 blockers and published only the counts; the classifier
was never committed, so for two days no per-blocker number here could be
checked. `_audit/_census/blocker-map.tsv` is the recovered part of that mapping.
**A map that can silently stop matching its own evidence is worse than no map --
it manufactures auditability**, which is the exact failure it was built to fix.
So the map is re-derived here from the evidence file and the census, and
compared line for line against what is committed.

THE RATCHET. `UNASSIGNED` may go DOWN -- somebody finding a committed source
that names more rows is the whole point, and this test must not stand in the way
of it. It may not go UP. A rise means evidence was deleted, an id stopped
resolving, or the ledger's tables moved, and every one of those is a thing
somebody should have to look at.

THE DANGEROUS DIRECTION IS ASSERTED SEPARATELY. No blocker may recount HIGHER
than the count the ledger published for it. A map with MORE rows in a set than
the ledger claims means a committed source and the ledger disagree about set
membership; that is a finding to be adjudicated by a person, never a merge to be
absorbed by a script.

SHOWN FAILING before it was admitted, in all four directions -- an instrument
that has only ever been green certifies nothing:

    delete one evidence line          -> UNASSIGNED 307 > 306, RATCHET fails
    add a fabricated 33rd GROUPS row  -> recount 2 > published 32 is not hit, but
                                         the map/evidence comparison fails
    add a second blocker for J 9      -> DOUBLE-ASSIGNED, build() reports it
    misspell an id (`J 999`)          -> UNRESOLVED, build() reports it
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_blocker_map as bbm  # noqa: E402

#: A CEILING, not a pin: see the module docstring. Lowered 306 -> 287 when two
#: further committed blocker-to-row tables were harvested
#: (`2026-09-05-settings-tail.md` section 2.3 and
#: `2026-09-05-routes-already-admitted.md`). Lowering it is the intended
#: direction and requires no ceremony; raising it needs a reason.
UNASSIGNED_CEILING = 287
FROZEN_GAP_ROWS = 409
LEDGER_BLOCKERS = 97


@pytest.fixture(scope="module")
def built():
    return bbm.build()


def test_the_evidence_resolves_and_no_row_carries_two_blockers(built):
    _gap, _current, _assign, problems = built
    assert problems == [], (
        "the assignment evidence no longer resolves against the census. Each "
        "line names the exact defect -- an id that matches no census row, an id "
        "that was not GAP at the freeze, or a row claimed by two blockers, "
        "which the ledger's own rule forbids (one blocker per row, the earliest "
        "binding constraint)."
    )


def test_the_frozen_row_set_is_still_the_set_the_ledger_divided(built):
    gap, _current, _assign, _problems = built
    assert len(gap) == FROZEN_GAP_ROWS, (
        f"the frozen census at {bbm.FROZEN_REF} now enumerates {len(gap)} GAP "
        f"rows, not {FROZEN_GAP_ROWS}. That commit is history and cannot have "
        "changed, so this means the ENUMERATOR changed -- which invalidates "
        "every per-blocker comparison in the map until somebody re-derives it."
    )


def test_the_ledger_tables_still_total_97_blockers_and_409_rows():
    published = bbm.ledger_counts()
    assert len(published) == LEDGER_BLOCKERS, (
        f"parsed {len(published)} blockers out of the ledger's tables, not "
        f"{LEDGER_BLOCKERS}. Either the tables were edited or the parse broke; "
        "the map's diff is meaningless against a set it cannot read."
    )
    assert sum(published.values()) == FROZEN_GAP_ROWS


def test_unassigned_only_ever_shrinks(built):
    gap, _current, assign, _problems = built
    unassigned = len(gap) - len(assign)
    assert unassigned <= UNASSIGNED_CEILING, (
        f"{unassigned} rows are UNASSIGNED, up from {UNASSIGNED_CEILING}. The "
        "map recovers row->blocker assignments from committed sources; a RISE "
        "means evidence was removed or stopped resolving. If a source was "
        "genuinely retracted, lower the ceiling deliberately and say why -- do "
        "not raise it to clear this."
    )


def test_no_blocker_recounts_higher_than_the_ledger_published(built):
    _gap, _current, assign, _problems = built
    published = bbm.ledger_counts()
    recount: dict[str, int] = {}
    for blocker, *_rest in assign.values():
        recount[blocker] = recount.get(blocker, 0) + 1
    over = {b: (n, published.get(b, 0))
            for b, n in recount.items() if n > published.get(b, 0)}
    assert over == {}, (
        f"these blockers hold MORE rows in the map than the ledger published: "
        f"{over}. That is a committed source and the ledger disagreeing about "
        "which rows are in a set. It is a finding for a person to adjudicate, "
        "not a number to absorb -- do not widen the published count to clear it."
    )


def test_the_committed_map_still_matches_what_the_evidence_derives(built):
    gap, current, assign, _problems = built
    committed = bbm.MAP_OUT.read_text(encoding="utf-8", errors="replace").splitlines()
    assert committed, "the map file is empty or missing"
    assert len(committed) - 1 == len(gap), (
        f"the committed map holds {len(committed) - 1} data lines against "
        f"{len(gap)} frozen GAP rows. Re-run "
        "`scripts/build_blocker_map.py --write`."
    )
    got = {}
    for line in committed[1:]:
        parts = line.split("\t")
        got[parts[0]] = (parts[1], parts[2])
    drift = []
    for rid in gap:
        want_b, want_k = (assign[rid][0], assign[rid][1]) if rid in assign \
            else ("UNASSIGNED", "UNASSIGNED")
        if got.get(rid) != (want_b, want_k):
            drift.append((rid, got.get(rid), (want_b, want_k)))
    assert drift == [], (
        f"{len(drift)} rows in the committed map no longer match what the "
        f"evidence derives, first three {drift[:3]}. The map is a DERIVED "
        "artifact: fix the evidence file, then re-run "
        "`scripts/build_blocker_map.py --write`. Never hand-edit the map."
    )


def test_the_state_today_column_reproduces_the_shipped_gap_total(built):
    """The map's two state columns must still close on the live count.

    409 frozen, less those that left, plus those that entered, is what
    `count_census_states.py` reports today. If this drifts, the map's
    `state_today` column has gone stale and the file is quietly claiming
    a reconciliation it no longer performs.
    """
    gap, current, _assign, _problems = built
    left = sum(1 for k in gap if current.get(k, "ROW-GONE") != "GAP")
    entered = [k for k, v in current.items() if v == "GAP" and k not in gap]
    derived = len(gap) - left + len(entered)
    live = sum(1 for v in current.values() if v == "GAP")
    assert derived == live, (
        f"the map reconciles to {derived} but the census holds {live} GAP rows "
        "today. Re-run `scripts/build_blocker_map.py --write`; the "
        "`state_today` column is stale."
    )
