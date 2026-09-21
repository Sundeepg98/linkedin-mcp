"""Pin the census ROW POPULATION by id, so the denominator cannot move in silence.

WHAT IS LOAD-BEARING AND WHAT NOTHING WAS HOLDING. `stated rows 704` is the
denominator under every completion figure this repository publishes. It is
quoted in 21 tracked documents and in two module docstrings. **Before this file
no shipped test asserted it.** `tests/test_census_rows_carry_a_state.py` checks
that a row in a state-bearing table carries a state; it cannot notice a row
being ADDED or DELETED, because it never counts. `count_census_states.py
--expect` controls the GAP numerator only, and it is not run by any gate.
So the denominator held for as long as everybody remembered to check it by hand,
which is the state an invariant is in just before it stops being true.

WHY AN ID SET AND NOT A SCALAR. A scalar pin can say `704 -> 705` and nothing
else, and the next question is always WHICH ROW -- a question that then costs
somebody a diff across four files totalling 592 KB. This pins the ID SET, so the
guard names the delta in its own failure message. That is the whole difference
between a tripwire and a report.

**IT PINS THE POPULATION, NEVER THE ADJUDICATION.** A row moving GAP ->
COVERED-PROVEN does NOT fire this guard, and must not: other waves move rows
every day and a guard that fired on each one would be switched off within the
week. What fires is a row ENTERING or LEAVING the set the counter can see --
which is exactly the event that silently rewrites every percentage in the
corpus.

MULTIPLICITY IS CARRIED, not collapsed to a set. `DUPLICATE-ROW-IS-MARKED-
NEVER-DELETED` (2026-09-20) rules that when two rows describe one capability the
duplicate STAYS in the file, marked. HEAD carries 704 rows and 704 distinct
(slice, id) pairs, so a set would be correct TODAY and wrong the first time that
ruling is exercised -- the second copy would vanish from the pin and the total
would disagree with it for a reason no message could explain. A `Counter` costs
nothing and cannot get that wrong.

IT IMPORTS THE SHIPPED ENUMERATOR. `enumerate_gap_rows.rows()` decides what a
stated row is and this file does not get a vote. Four waves reimplemented a
shipped census parser on 2026-09-05 and three got a broken one; one disagreed
with the shipped count by 66 rows. THE CONSEQUENCE IS STATED RATHER THAN HIDDEN:
this pin inherits that parse's blind spots exactly. A row whose state cell is
prose is invisible to the enumerator and is therefore invisible here -- it is
not in the pin, and a later repair of such a cell will fire this guard as an
ADDED row, which is correct and is the point.

A DIALECT IS COLLECTED, NEVER SWALLOWED. `rows()` refuses outright unless the
caller takes a `dialects` list; this file takes one and REFUSES TO WRITE A PIN
while any dialect is open, because a pin taken over a census with an unreadable
state cell would freeze a denominator that is already short by that row.

    python scripts/pin_census_rows.py            # report, exit 0
    python scripts/pin_census_rows.py --check    # fail on any drift, exit 1
    python scripts/pin_census_rows.py --write    # re-pin, printing the delta

**`--write` IS NOT A WAY TO CLEAR A RED GUARD.** It prints what moved and
requires the same thing the tool-surface pin requires: in the SAME commit, say
what changed the census population and why. The guard buys the moment; a human
supplies the judgement. See `tests/test_the_census_row_total_is_pinned.py`.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import count_census_states as ccs  # noqa: E402  (the shipped counter)
import enumerate_gap_rows as egr  # noqa: E402  (the shipped enumerator)

#: The pin lives beside the tests that read it, with the other baselines
#: (`reader_leak_baseline.json`, `tool_envelope_baseline.json`). It is NOT put
#: in `_audit/_census/` on purpose: that directory is the census itself, and a
#: pin stored inside the thing it pins is one careless bulk edit away from
#: being updated by the same hand that moved the rows.
PIN = _HERE.parents[0] / "tests" / "census_row_pin.json"


class DialectOpen(Exception):
    """A state cell is spelled in a dialect, so the population is already short."""


def population(ref: str | None = None) -> collections.Counter:
    """Counter of (slice_letter, row_id) over every STATED row.

    Raises `DialectOpen` rather than returning a short count: a dialect removes
    its row from numerator and denominator at the same instant, and pinning
    that total would write the defect into the baseline as though it were the
    census.
    """
    dialects: list[str] = []
    rows = list(egr.rows(ref=ref, dialects=dialects))
    if dialects:
        raise DialectOpen(
            f"{len(dialects)} state cell(s) are spelled in a dialect the shipped "
            f"vocabulary does not hold. The census population is SHORT by that "
            f"many rows right now, so no pin taken here would describe the "
            f"census.\n  " + "\n  ".join(dialects)
        )
    return collections.Counter((letter, rid) for letter, rid, *_ in rows)


def per_slice(pop: collections.Counter) -> dict[str, int]:
    out: dict[str, int] = {letter: 0 for letter in ccs.SLICES}
    for (letter, _rid), n in pop.items():
        out[letter] = out.get(letter, 0) + n
    return out


def load() -> collections.Counter:
    """The pinned population, as a Counter, or an empty one if unpinned."""
    if not PIN.exists():
        return collections.Counter()
    raw = json.loads(PIN.read_text(encoding="utf-8"))
    return collections.Counter(
        {(letter, rid): n
         for letter, ids in raw["rows"].items()
         for rid, n in ids.items()}
    )


def dump(pop: collections.Counter) -> str:
    """The pin as sorted JSON -- stable, so a diff shows only what moved."""
    rows: dict[str, dict[str, int]] = {}
    for (letter, rid), n in pop.items():
        rows.setdefault(letter, {})[rid] = n
    body = {
        "_comment": (
            "PINNED CENSUS ROW POPULATION. Generated by "
            "scripts/pin_census_rows.py --write; asserted by "
            "tests/test_the_census_row_total_is_pinned.py. This is the "
            "DENOMINATOR every completion figure in this repository divides "
            "by. It pins WHICH rows exist, never what state they are in -- a "
            "row moving GAP to COVERED-PROVEN does not belong in this diff."
        ),
        "total": sum(pop.values()),
        "per_slice": {k: v for k, v in sorted(per_slice(pop).items())},
        "rows": {
            letter: {rid: n for rid, n in sorted(ids.items())}
            for letter, ids in sorted(rows.items())
        },
    }
    return json.dumps(body, indent=2, sort_keys=False) + "\n"


def delta(pinned: collections.Counter, live: collections.Counter):
    """(added, removed) as sorted [(letter, id, how_many)] lists."""
    added, removed = [], []
    for key in sorted(set(pinned) | set(live)):
        diff = live[key] - pinned[key]
        if diff > 0:
            added.append((key[0], key[1], diff))
        elif diff < 0:
            removed.append((key[0], key[1], -diff))
    return added, removed


def id_still_in_slice(letter: str, row_id: str) -> bool:
    """Does this row id still appear as a table row in its slice file?

    THE DISCRIMINATOR, and the reason this guard can say WHY a row left. A row
    can leave the counted population two entirely different ways and they need
    opposite fixes:

      * the row was DELETED from the markdown          -- a census edit
      * the row is still there, but its STATE CELL is no longer a state the
        shipped vocabulary can read -- the row silently left the denominator
        while looking, in the file, exactly as it always did

    Reported identically they are indistinguishable, and the second is the one
    that has actually happened in this repository twice (`XR`, `CANNOT-DELIVER`).
    """
    path = ccs.CENSUS / ccs.SLICES[letter]
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|"):
            continue
        c = ccs.cells(line)
        if len(c) < 3 or not ccs.ROW.match(line):
            continue
        if c[0] == row_id:
            return True
    return False


#: A real drift is a handful of rows; anything larger is a bulk edit or an
#: absent pin, and 700 identical lines would bury the one that matters. The
#: count is always printed in full above, so the cap truncates the NAMING and
#: never the measurement.
_MAX_NAMED = 40


def describe(added, removed) -> str:
    """The failure text. It names the delta, because a total cannot."""
    out: list[str] = []
    for letter, rid, n in added:
        out.append(f"  ADDED    {letter} {rid}"
                   + (f" (x{n})" if n > 1 else "")
                   + " -- a capability row entered the census. Every published "
                     "percentage divides by a different number than it did.")
    for letter, rid, n in removed:
        if id_still_in_slice(letter, rid):
            out.append(
                f"  UNREADABLE {letter} {rid}"
                + (f" (x{n})" if n > 1 else "")
                + " -- THE ROW IS STILL IN THE FILE but its state cell is no "
                  "longer a state the shipped vocabulary can read. It has left "
                  "the numerator AND the denominator with no diff that looks "
                  "like a state change. Fix the cell, or teach "
                  "`count_census_states.STATES` the spelling WITH a receipt.")
        else:
            out.append(
                f"  DELETED  {letter} {rid}"
                + (f" (x{n})" if n > 1 else "")
                + " -- the row is gone from its slice. `DUPLICATE-ROW-IS-"
                  "MARKED-NEVER-DELETED` says a census row is marked, never "
                  "removed; if this deletion is intended, say so in the commit.")
    if len(out) > _MAX_NAMED:
        hidden = len(out) - _MAX_NAMED
        out = out[:_MAX_NAMED] + [
            f"  ... and {hidden} more row(s) not named here. Run "
            f"`python scripts/pin_census_rows.py` for the full list. A delta "
            f"this large is a bulk edit or an absent pin, not a drift."]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pin the census row population.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 on any drift from the pin")
    ap.add_argument("--write", action="store_true",
                    help="re-pin to the working tree, printing the delta")
    args = ap.parse_args(argv)

    try:
        live = population()
    except DialectOpen as exc:
        print(f"REFUSED -- {exc}")
        return 1

    pinned = load()
    added, removed = delta(pinned, live)

    print(f"pin          {PIN.relative_to(_HERE.parents[0]).as_posix()}"
          f"{'' if PIN.exists() else '   (ABSENT -- nothing is pinned)'}")
    print(f"pinned rows  {sum(pinned.values()):4d}")
    print(f"live rows    {sum(live.values()):4d}")
    for letter in sorted(ccs.SLICES):
        print(f"  {letter}  {ccs.SLICES[letter]:28s} "
              f"pinned {per_slice(pinned).get(letter, 0):4d}   "
              f"live {per_slice(live).get(letter, 0):4d}")

    if added or removed:
        print(f"\nTHE CENSUS POPULATION MOVED: "
              f"{len(added)} added, {len(removed)} removed "
              f"(total {sum(pinned.values())} -> {sum(live.values())})")
        print(describe(added, removed))
    else:
        print("\nno drift: the live census population is exactly the pin")

    if args.write:
        PIN.write_text(dump(live), encoding="ascii")
        print(f"\nwrote {PIN}")
        print("NOW SAY WHAT MOVED, IN THIS COMMIT. A re-pin is a review moment, "
              "not a way to clear a red guard.")
        return 0
    if args.check:
        return 1 if (added or removed) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
