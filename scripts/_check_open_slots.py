"""How many of the UNASSIGNED rows can EVER be filed, and how many cannot.

WHY THIS EXISTS. `build_blocker_map.py` prints "assigned 388 / UNASSIGNED 21"
and, separately, a per-blocker deficit. Both numbers are correct and the pair
invites a false inference that has already cost this census two cycles: that
21 open slots and 21 unassigned rows will pair up. THEY DO NOT. Some open
slots hold a row that a committed source has moved elsewhere (`RE_FILED`);
others have been RULED to have no referent inside the 409 at all. Subtract
those and the fillable slot count drops BELOW the unassigned row count, so a
computable number of rows can never be filed by anybody.

WHAT IT IS NOT. Not a gate. It asserts nothing about the map's content and
changes no file. The one thing it does assert is its own arithmetic, below.

AND ITS UNASSIGNED COUNT IS NOT TODAY'S SET OF UNROUTED ROWS. Everything here
is scoped to the FROZEN 409, which is what the control exists to keep true --
mixing the frozen set with the live census is the "two different populations"
error this file was written to prevent. So a row that entered GAP AFTER the
freeze has no line in the map, and therefore cannot appear in the UNASSIGNED
bucket, nor even among the rows ruled unfileable: being unfileable still
requires being IN the map. Measured 2026-09-21 -- today that is exactly one
row, `P L2b`, split out of the compound `L2` on 2026-09-04, the day after the
2026-09-03 freeze, and the map's own prose says of it that "no map edit can
fix that".

THAT DRIFT IS ALREADY REPORTED, NEXT DOOR, and this note exists only so the
reader looks there instead of concluding it is unmeasured. `build_blocker_map.py`
prints rows LEFT, rows ENTERED and today's derived GAP total on every run, from
the `frozen`/`current` pair it already builds. Read that before treating the
number below as a count of what is unrouted now.

THE CONTROL, and it must fire. The ledger's published counts, the map's data
lines and the frozen GAP total are three independently produced numbers that
must all read 409 -- the ledger because it claims a PARTITION of the frozen
GAP set, the map because it enumerates that same set. If any of the three
drifts, every "open slot" figure below is measuring two different populations
against each other and the report raises instead of printing. Shown failing:
`--selftest` perturbs one published count by +1 and the control raises.

THE RULED-PHANTOM TABLE below is the part a reader must keep current. A slot
enters it when a committed ruling or a measured wave verdict says the
published row has no referent anywhere in the 409. It is deliberately NOT
inferred -- an empty slot is not evidence that its row does not exist.

Run:  ./venv/Scripts/python.exe scripts/_check_open_slots.py
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_blocker_map as B  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAP = ROOT / "_audit" / "_census" / "blocker-map.tsv"

#: Open slots a committed source says have NO referent inside the 409.
#: Each entry names the document that ruled or measured it. These are not
#: fillable by any future wave, so they are removed from the fillable count.
RULED_PHANTOM: dict[str, tuple[int, str]] = {
    "CREATOR-HUB-SURFACE": (
        1, "_audit/2026-09-19-the-five-requests-ruled.md section E -- RULED a "
           "ledger over-count by the box, after the published-split check "
           "showed neither over-published neighbour holds a creator-hub row"),
    "POST-COMMENT-CONTROLS": (
        1, "_audit/2026-09-19-the-five-requests-ruled.md section E -- same "
           "ruling, same instrument"),
    "FOUND-A-JOB-FLOW": (
        1, "_audit/2026-09-19-the-four-absent-blockers.md section 3 -- wave "
           "verdict: the capability's only row (P I16) is load-bearing inside "
           "OPEN-TO-WORK-MODAL's 11 and the ledger's own closed 120-sum"),
    "MESSAGE-ADDRESSING": (
        1, "_audit/2026-09-19-the-four-absent-blockers.md section 4 -- wave "
           "verdict: its only named row (M M1) was never in the 409, measured "
           "with the shipped counter and controls firing both ways"),
}


def measure(published: dict[str, int], frozen_gap: int) -> dict[str, object]:
    rows = MAP.read_text(encoding="ascii", errors="replace").splitlines()[1:]
    held: dict[str, int] = {}
    unassigned: list[str] = []
    for line in rows:
        cells = line.split("\t")
        if cells[1] == "UNASSIGNED":
            unassigned.append(cells[0])
        else:
            held[cells[1]] = held.get(cells[1], 0) + 1

    pub_total = sum(published.values())
    if not pub_total == len(rows) == frozen_gap:
        raise SystemExit(
            "CONTROL FAILED -- the ledger's published total "
            f"({pub_total}), the map's data lines ({len(rows)}) and the "
            f"frozen GAP set ({frozen_gap}) must all agree. They do "
            "not, so no open-slot figure below would be comparable.")

    open_slots, refiled, phantom = [], 0, 0
    for blocker in sorted(published):
        deficit = published[blocker] - held.get(blocker, 0)
        if deficit <= 0:
            continue
        moved = len(B.RE_FILED.get(blocker, {}))
        ruled = RULED_PHANTOM.get(blocker, (0, ""))[0]
        refiled += moved
        phantom += ruled
        open_slots.append((blocker, published[blocker], held.get(blocker, 0),
                           deficit, moved, ruled))
    total_open = sum(s[3] for s in open_slots)
    return {
        "open_slots": open_slots, "total_open": total_open,
        "refiled": refiled, "phantom": phantom,
        "fillable": total_open - refiled - phantom,
        "unassigned": unassigned,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="perturb one published count and show the control "
                         "refusing to report")
    args = ap.parse_args()

    published = B.ledger_counts()
    frozen_gap = len(B.build()[0])
    if args.selftest:
        victim = sorted(published)[0]
        published[victim] += 1
        print(f"SELFTEST: {victim} published count perturbed +1. "
              "The control must now refuse.")

    m = measure(published, frozen_gap)
    print(f"{'blocker':32s} {'pub':>4s} {'held':>5s} {'open':>5s}  why the "
          f"open slot is there")
    for blocker, pub, held, deficit, moved, ruled in m["open_slots"]:
        why = []
        if moved:
            why.append(f"{moved} RE_FILED elsewhere")
        if ruled:
            why.append(f"{ruled} RULED PHANTOM")
        rest = deficit - moved - ruled
        if rest:
            why.append(f"{rest} fillable")
        print(f"  {blocker:30s} {pub:4d} {held:5d} {deficit:5d}  "
              f"{', '.join(why)}")

    print(f"\n  open slots, total                    {m['total_open']:3d}")
    print(f"  ... whose row is filed elsewhere     {m['refiled']:3d}")
    print(f"  ... RULED to have no referent        {m['phantom']:3d}")
    print(f"  FILLABLE SLOTS                       {m['fillable']:3d}")
    print(f"  UNASSIGNED ROWS                      {len(m['unassigned']):3d}")
    short = len(m["unassigned"]) - m["fillable"]
    print(f"\n  ROWS THAT CAN NEVER BE FILED         {short:3d}"
          "   <- no slot exists for them anywhere in the ledger")
    print("\n  unassigned: " + " | ".join(m["unassigned"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
