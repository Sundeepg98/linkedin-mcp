"""`RE_FILED` FIXES THE SOURCE BLOCKER AND CREDITS THE DESTINATION TWICE.

WHAT `RE_FILED` DOES. `build_blocker_map.py` compares each blocker's AT-HEAD
holdings against the ledger's published count for that blocker. When a row the
ledger counted under blocker X now lives at blocker Y, X is short by one through
no fault of the search -- so `RE_FILED` records the move and X reads ACCOUNTED
instead of PARTIAL. That half is right and it is what the 2026-09-19 convention
ruling was for.

WHAT NOTHING DOES. The row still counts toward Y's total. Y did not publish it,
but Y is credited for it, so an INCOMING re-file silently pays for one of Y's
OWN published rows that nobody recovered. The verdict then prints
*"COMPLETE -- every published row recovered"* over a blocker that has not
recovered them.

THIS IS NOT SYMMETRICAL WITH THE SOURCE FIX AND THAT IS THE WHOLE POINT. A
re-file is count-neutral ACROSS THE PAIR, which is exactly why no count
assertion anywhere can see it -- the same structural blindness
`_check_published_split.py` was written for, one level up. The split check
catches it only when the moved rows happen to change a direction tally; this
catches it directly, by name.

MEASURED at `da72649`: `SEARCH-RESULTS-SURFACE` publishes 21, holds 21, and 4 of
those 21 were published by three OTHER blockers -- its own recovery is 17 of 21.
`FEED-PREFERENCES` publishes 1, holds 1, and that single row was published by
`HASHTAG-EXISTENCE` -- its own recovery is 0 of 1, printed as COMPLETE.

IT IS A REPORT, NOT A GATE. The moves themselves were ruled deliberate; what is
undeclared is the credit they hand the destination. Promote to an assertion once
each destination's own shortfall is either recovered or written down.

CONTROL, because a check that cannot fail certifies nothing: `--control` adds a
synthetic incoming re-file to a blocker this report does NOT currently name, and
requires the report to name it.

    ./venv/Scripts/python.exe scripts/_check_refile_destination_credit.py
    ./venv/Scripts/python.exe scripts/_check_refile_destination_credit.py --control
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_blocker_map as bbm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: A blocker the real data does NOT name, used only by `--control`. Injecting
#: into one already named would measure the baseline rather than the instrument.
CONTROL_VICTIM = "GROUPS-SURFACE"
CONTROL_ROW = "N 63"


def publishers(extra: tuple[str, str, str] | None = None) -> dict[str, tuple[str, str]]:
    """{row id: (blocker that PUBLISHED it, blocker RE_FILED says it went to)}."""
    out: dict[str, tuple[str, str]] = {}
    for src, moved in bbm.RE_FILED.items():
        for rid, why in moved.items():
            out[rid] = (src, why.split(" -- ")[0].strip())
    if extra is not None:
        rid, src, dest = extra
        out[rid] = (src, dest)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--control", action="store_true",
                    help="inject a synthetic incoming re-file and require it be named")
    args = ap.parse_args(argv)

    gap, _cur, assign, problems = bbm.build()
    published = bbm.ledger_counts()
    for p in problems:
        print(f"  FAIL upstream: {p}")

    extra = None
    if args.control:
        extra = (CONTROL_ROW, "CONTROL-SYNTHETIC-SOURCE", CONTROL_VICTIM)
    pub_by = publishers(extra)

    held: dict[str, int] = {}
    incoming: dict[str, list[str]] = {}
    for rid, (blocker, *_rest) in assign.items():
        held[blocker] = held.get(blocker, 0) + 1
        if rid in pub_by:
            incoming.setdefault(blocker, []).append(rid)

    print(f"rows RE_FILED                     {len(pub_by)}")
    for rid, (src, dest) in sorted(pub_by.items()):
        at_head = assign.get(rid, ("UNASSIGNED",))[0]
        note = "" if at_head == dest else f"   MISMATCH: table says {dest}, map holds {at_head}"
        print(f"  {rid:8s} published by {src:24s} held by {at_head}{note}")

    print("\ndestinations, and what their own recovery is once incoming rows are debited")
    print(f"  {'blocker':28s} {'pub':>4s} {'held':>5s} {'in':>3s} {'own':>4s} {'own vs pub':>11s}  printed verdict")
    named: list[str] = []
    for b in sorted(incoming):
        own = held[b] - len(incoming[b])
        d = own - published.get(b, 0)
        printed = "COMPLETE" if held[b] == published.get(b, 0) else "not COMPLETE"
        flag = "  <-- COMPLETE IS FALSE" if (printed == "COMPLETE" and d < 0) else ""
        named.append(b)
        print(f"  {b:28s} {published.get(b,0):4d} {held[b]:5d} "
              f"{len(incoming[b]):3d} {own:4d} {d:+11d}  {printed}{flag}")
        print(f"     incoming: {', '.join(sorted(incoming[b]))}")

    masked = sum(len(v) for b, v in incoming.items()
                 if held[b] == published.get(b, 0) and held[b] - len(v) < published.get(b, 0))
    print(f"\ndestinations carrying incoming rows          {len(incoming)}")
    print(f"published rows masked by an incoming credit   {masked}")

    if args.control:
        ok = CONTROL_VICTIM in named
        print(f"\ncontrol: injected an incoming re-file at {CONTROL_VICTIM} -- "
              f"{'NAMED, the report can fail' if ok else 'NOT NAMED -- BROKEN'}")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
