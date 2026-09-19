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

SHOWN FAILING in five directions -- an instrument that has only ever been green
certifies nothing. Four were planted before admission; the fifth arrived on its
own an hour later and is the one worth reading:

    delete one evidence line             ratchet + map-drift red
    double-assign an already-mapped row  DOUBLE-ASSIGNED
    plant an id matching no census row   UNRESOLVED
    plant a 2nd row on a 1-row blocker   over-count + map-drift red
    break the ledger table header anchor "blockers the parse does not know"

The fifth was not a mutation. A neighbouring wave appended 19 lines to the
ledger, both its tables slid 28 rows down, and `ledger_counts()` -- then a
hardcoded line window -- lost one of them. See the comment in
`test_no_blocker_recounts_higher_than_the_ledger_published`.
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
#: `2026-09-05-routes-already-admitted.md`), then 287 -> 284 when a recall check
#: on the scan found one row list the equality filter had skipped, then
#: 284 -> 278 from a whole-tracked-corpus scan (not ledger-and-amendments only)
#: whose raw 128-CONTRADICTS / 19-NEW output was cut by a proximity-plus-same-
#: paragraph filter to 22 and 6 respectively, then each of the 6 survivors read
#: by hand before being added -- all six RECON-DOC, none the ledger itself
#: (GROUPS-SURFACE M C61/N 63/N 163, SEARCH-RESULTS-SURFACE M C70/N 161,
#: NEWSLETTER-SURFACE N 57). The 22 refined CONTRADICTS were left for a person,
#: not absorbed. Lowering it is the intended direction and requires no
#: ceremony; raising it needs a reason.
#:
#: 278 -> 268 on 2026-09-19, SEVEN rows, three blockers taken from ABSENT to
#: COMPLETE. `M C2` to PUBLISH-POST-AUDIENCE-PARAM (1 of 1) -- amendment A3 is
#: HEADED with the blocker name and states the row verbatim inside it, so the
#: map's "no committed source names this row against any blocker" was false
#: twice over. `M C10` and `M C28` to MENTION-COMPOSITION-RULING (2 of 2) --
#: `2026-09-05-article-publish.md:130` names the pair and ties it to "exactly
#: blocker 16's count of two", and rank 16 IS that blocker. `M C54 C55 C56 C76`
#: to COLLABORATIVE-CONTENT (4 of 4) -- its section 4 enumerates that blocker's
#: four rows in one sentence.
#:
#: ONE OF THOSE SEVEN WAS REPORTED AGAINST THE WRONG BLOCKER AND THIS CEILING IS
#: WHY IT MATTERS. `M C55` was relayed as assignable to MENTION-COMPOSITION-
#: RULING alongside C10 and C28. That blocker publishes TWO rows, C10 and C28
#: close it exactly, and a third would have tripped the over-count assertion
#: rather than this one -- the two guards catch different halves, and the
#: dangerous half is the other one. C55 is a collaborators row, not a mention
#: row.
UNASSIGNED_CEILING = 268
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
    # SEPARATE THE TWO CAUSES BEFORE REPORTING EITHER. A blocker absent from the
    # parse is not a blocker published at zero, and collapsing them makes a
    # PARSER failure wear a DATA disagreement's costume. Measured 2026-09-05:
    # a neighbouring wave appended 19 lines to the ledger, the cost-0 table slid
    # out of a hardcoded line window, and four blockers read as published 0 --
    # this assertion fired and named the wrong cause. It names both now.
    unknown = sorted(b for b in recount if b not in published)
    assert unknown == [], (
        f"the map holds blockers the ledger parse does not know at all: "
        f"{unknown}. Before treating this as a disagreement, check that BOTH "
        "ledger tables still parse -- `build_blocker_map.ledger_counts()` "
        "locates them by header row, and a renamed or reformatted header "
        "returns a partial parse rather than an error."
    )
    over = {b: (n, published[b]) for b, n in recount.items() if n > published[b]}
    assert over == {}, (
        f"these blockers hold MORE rows in the map than the ledger published "
        f"(map, published): {over}. That is a committed source and the ledger "
        "disagreeing about which rows are in a set. It is a finding for a "
        "person to adjudicate, not a number to absorb -- do not widen the "
        "published count to clear it."
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
