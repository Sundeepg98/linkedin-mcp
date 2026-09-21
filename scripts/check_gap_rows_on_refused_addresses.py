"""A GAP row naming an address the read gate REFUSES is filed against this
census's own named bar for EXCLUDED-RULED.

THE DEFECT, STATED SO IT CAN BE ARGUED WITH. A census row records its blocker
in prose, and a great many of those blockers are claims ABOUT THE BOUNDARY --
"no forbidden substring catches it", "caught by no substring", "named nowhere
in this repo". **Those are measurements with a timestamp, and nothing in this
census re-takes them.** The boundary is edited: ten entries were added to
`readonly._FORBIDDEN_URL_SUBSTRINGS` on 2026-09-03, the day after
`profile.md` was written, and the census was never re-read against them.

Measured 2026-09-20 over the 101 write-direction GAP rows of `profile.md` and
`network.md`: **FOUR such claims were false**, and two of the three addresses
they concern are NAMED VERBATIM in the boundary's own comment as the members
that motivated the entry:

    /public-profile/settings   claimed uncaught   -> refused on `settings`
    /uas/login                 claimed uncaught   -> refused on `/uas/`
    /badges/profile/create     claimed uncaught   -> refused on `/create`

WHY THE CHECK IS NOT A PROSE PARSER, AND THIS IS THE LOAD-BEARING CHOICE. The
obvious implementation matches the negative claim -- "no forbidden substring",
"not on the allowlist" -- and convicts the cell that carries it. **That
implementation is wrong here and this repository has already paid for the same
mistake once**: the reopener guard's first version reused a reporter's
case-insensitive `REOPEN(ER|S)` matcher and went green on cells reading *"the
Help-article half REOPENS NOTHING"*. The mirror of that trap lives here. `N 38`
and `N 44` QUOTE their own superseded negative claim and then correct it in the
next sentence; a matcher aimed at the claim convicts the two rows that already
did the right thing, and clears the rows that never noticed.

So this check never reads a claim. It reads the ADDRESS and asks the SHIPPED
GATE, `readonly.assert_read_url`, and it is interested only in a refusal that
names a FORBIDDEN SUBSTRING -- never in allowlist silence, which `network.md`
section 2 says explicitly is not a reason.

THE BAR IT ENFORCES IS THE CENSUS'S OWN, quoted from the `N 38` cell:

    A forbidden-substring entry is this census's own named bar for
    EXCLUDED-RULED.

    python scripts/check_gap_rows_on_refused_addresses.py
    python scripts/check_gap_rows_on_refused_addresses.py --expect-gap 4
    python scripts/check_gap_rows_on_refused_addresses.py --demonstrate-red

=============================================================================
IT IS A REPORTER WITH A PINNED CONTROL, NOT A GATE, AND THE REASON IS NAMED
=============================================================================

At HEAD five GAP rows still sit on a refused address, and every one of them is
outside the wave that wrote this file: `M M11` and `M C88` belong to the
messaging slice, `N A3` and `N A5` are READ-direction rows, and `P D25` is a
MENU-CONTENTS row naming three substrings at once rather than resting on one
address. **Shipping this as a hard gate would mean ruling on rows this wave was
not scoped to, so it ships PINNED instead**: `--expect-gap N` fails when the
count moves in EITHER direction, which makes both a new offender and a silent
fix loud. A gate that claims a scope nobody ruled is the half-truth this
repository refuses.

THE UNIT IS A ROW, NOT AN ADDRESS, AND THAT DISTINCTION COST A WRONG PIN ONCE
ALREADY -- the first reading of this said EIGHT, which was (row, address)
PAIRS: `P D25` alone carries three. A count whose unit is not stated is a
count that will be compared against a different one.

FOUR WAYS THIS COULD HAVE BEEN A CHECK THAT CANNOT FAIL:

1. **AN EMPTY WALK WOULD PASS.** So it asserts PER SLICE that the file yielded
   at least one stated row, and a zero is a loud failure naming the file. Per
   slice and never over the union: a union assertion over a redundant corpus
   cannot detect a lost source.
2. **A GATE THAT NEVER REFUSES WOULD PASS.** So it asserts that the shipped
   gate refused at least one address in the run, and reports how many it
   admitted. An `assert_read_url` mutated into a no-op would otherwise read as
   a clean census.
3. **IT WOULD CLAIM MORE THAN IT RAN.** Every run prints the non-GAP states it
   found on refused addresses, by name and count -- they are the evidence the
   bar is real practice and not this file's invention -- and prints the
   addresses it could not classify.
4. **THE VERDICT COULD BE RIGHT WHILE THE WALK FINDS NOTHING.**
   `--demonstrate-red` plants a GAP row carrying a refused address into a COPY
   of the real census, repoints the walker, and proves the row is FOUND and
   CONVICTED end to end -- and plants a second row carrying an ADMITTED address
   to prove the check discriminates rather than merely refusing.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from linkedin_server import readonly          # noqa: E402
import count_census_states as ccs             # noqa: E402

#: A backticked path token. Deliberately NOT a bare-prose matcher: an
#: unbackticked `/edit/` in a sentence is a mention, and this check is about
#: addresses a row rests on.
ADDR = re.compile(r"`(/[A-Za-z0-9_/\-]{4,}[A-Za-z0-9_/\-])`")
#: The gate's own words when it refuses on the substring list rather than on
#: the allowlist. Read from the message so the two cannot drift apart silently;
#: a message change makes this check report UNCLASSIFIED, never a false pass.
NAMES_SUBSTRING = re.compile(r"contains '([^']+)'")

#: Planted rows for the red. Built from addresses the SHIPPED tuple already
#: holds, so the red proves the REAL rule fires rather than one written to fire.
PLANTED_REFUSED = ("| 9801 | PLANTED CONTROL ROW -- not a capability | W | GAP "
                   "| blocker: `/public-profile/settings`, a planted row |")
PLANTED_ADMITTED = ("| 9802 | PLANTED CONTROL ROW -- admitted address | W | GAP "
                    "| blocker: `/jobs/search/`, a planted row |")


class Finding:
    __slots__ = ("letter", "rid", "state", "lineno", "addr", "entry", "capability")

    def __init__(self, letter, rid, state, lineno, addr, entry, capability):
        self.letter, self.rid, self.state, self.lineno = letter, rid, state, lineno
        self.addr, self.entry, self.capability = addr, entry, capability

    @property
    def key(self) -> str:
        return f"{self.letter} {self.rid}"


def verdict(addr: str) -> tuple[str, str]:
    """(what the shipped gate did, the forbidden entry it named or '')."""
    url = addr if addr.startswith("http") else "https://www.linkedin.com" + addr
    try:
        readonly.assert_read_url(url)
    except Exception as exc:                                   # noqa: BLE001
        m = NAMES_SUBSTRING.search(str(exc))
        if m:
            return "REFUSED-SUBSTRING", m.group(1)
        return "REFUSED-ALLOWLIST", ""
    return "ADMITTED", ""


def walk() -> tuple[list[Finding], dict[str, int], dict[str, int]]:
    """(findings, rows read per slice, gate verdict tally)."""
    findings: list[Finding] = []
    per_slice: dict[str, int] = {}
    tally: dict[str, int] = {}
    for letter, name in ccs.SLICES.items():
        rows = 0
        path = ccs.CENSUS / name
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not line.startswith("|"):
                continue
            c = ccs.cells(line)
            if len(c) < 3 or (c[0] and set(c[0]) <= set("-: ")):
                continue
            if not ccs.ROW.match(line) or c[0].lower() in ccs.HEADERS:
                continue
            state, _ = ccs.classify(c)
            if not state and letter == "N" and re.fullmatch(r"A\d+", c[0]):
                state = "GAP"
            if not state:
                continue
            rows += 1
            for addr in sorted(set(ADDR.findall(" ".join(c[3:])))):
                got, entry = verdict(addr)
                tally[got] = tally.get(got, 0) + 1
                if got == "REFUSED-SUBSTRING":
                    findings.append(Finding(letter, c[0], state, lineno,
                                            addr, entry, c[1]))
        per_slice[name] = rows
    return findings, per_slice, tally


def run(expect_gap: int | None) -> tuple[bool, list[str]]:
    out: list[str] = []
    failed = False
    findings, per_slice, tally = walk()

    # --- HOLE 1: an empty walk must be loud, and PER SLICE -----------------
    out.append("PER-SLICE LIVENESS -- a slice yielding zero stated rows means it")
    out.append("stopped being parsed, not that it got clean:")
    for name, n in per_slice.items():
        if n == 0:
            out.append(f"  FAIL  {name}: 0 stated rows. Either this file is no "
                       f"longer parsed or the census changed shape. Both need a "
                       f"human; neither is a pass.")
            failed = True
        else:
            out.append(f"  ok    {name}: {n} stated rows read")

    # --- HOLE 2: a gate that never refuses must be loud --------------------
    out.append("")
    out.append("GATE LIVENESS -- readonly.assert_read_url verdicts this run:")
    for got in sorted(tally):
        out.append(f"  {got:<22} {tally[got]:4d}")
    if not tally.get("REFUSED-SUBSTRING"):
        out.append("  FAIL  the shipped gate refused NOTHING on a forbidden "
                   "substring in this entire run. A gate mutated into a no-op "
                   "reads exactly like a clean census from here.")
        failed = True

    gap = [f for f in findings if f.state == "GAP"]
    other = [f for f in findings if f.state != "GAP"]

    # --- the verdict -------------------------------------------------------
    out.append("")
    out.append("GAP ROWS ON AN ADDRESS THE READ GATE REFUSES ON A SUBSTRING")
    seen: set[str] = set()
    for f in sorted(gap, key=lambda f: (f.letter, f.lineno)):
        if f.key in seen:
            continue
        seen.add(f.key)
        entries = sorted({g.entry for g in gap if g.key == f.key})
        out.append(f"  {f.key:<9} {ccs.SLICES[f.letter]}:{f.lineno}")
        out.append(f"            {f.capability[:64]}")
        out.append(f"            refused on {', '.join(repr(e) for e in entries)}")
    if not gap:
        out.append("  none - no GAP row in the census names an address the gate "
                   "refuses on a forbidden substring")
    out.append(f"  distinct GAP rows: {len(seen)}")

    if expect_gap is not None:
        ok = len(seen) == expect_gap
        out.append("")
        out.append(f"CONTROL: expected {expect_gap}, measured {len(seen)} -- "
                   f"{'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            out.append("  A MOVE IN EITHER DIRECTION IS LOUD ON PURPOSE. More "
                       "means a new row was filed GAP against this census's own "
                       "named bar for EXCLUDED-RULED; fewer means somebody "
                       "resolved one and did not re-pin the count, which is how "
                       "a control quietly stops controlling anything.")
        failed = failed or not ok

    # --- HOLE 3: say what was NOT checked ----------------------------------
    out.append("")
    out.append("NOT CHECKED BY THIS RUN, stated rather than left to look like coverage:")
    states: dict[str, set[str]] = {}
    for f in other:
        states.setdefault(f.state, set()).add(f.key)
    for st in sorted(states):
        out.append(f"  {st:<24} {len(states[st]):3d} rows on a refused address -- "
                   f"already past the bar")
    out.append(f"  {'ADMITTED addresses':<24} {tally.get('ADMITTED', 0):3d} -- a row "
               f"may still be GAP for reasons this check")
    out.append(f"  {'':<24}     cannot see; it only reads the boundary")
    out.append(f"  {'ALLOWLIST-ONLY refusals':<24} "
               f"{tally.get('REFUSED-ALLOWLIST', 0):3d} -- deliberately ignored: "
               f"allowlist silence")
    out.append(f"  {'':<24}     is not a reason (network.md section 2)")
    out.append("  PROSE, every claim a cell makes about the boundary -- this check")
    out.append("       reads ADDRESSES and never claims, for the reason in the")
    out.append("       docstring")
    return failed, out


def demonstrate_red() -> int:
    print("DEMONSTRATE-RED -- this check must be able to CONVICT, and must also")
    print("be able to CLEAR. A rule that refuses everything is not discriminating,")
    print("it is just failing.\n")
    ok = True
    real = ccs.CENSUS
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="gap-refused-red-"))
    try:
        for name in ccs.SLICES.values():
            shutil.copy2(real / name, tmp / name)
        target = tmp / ccs.SLICES["J"]
        lines = target.read_text(encoding="utf-8").splitlines()
        at = None
        for i, line in enumerate(lines):
            if line.startswith("| 1 |") and "|" in line[5:]:
                at = i + 1
                break
        if at is None:
            print("  CONTROL BROKEN: no table row to plant beside")
            return 1
        lines.insert(at, PLANTED_ADMITTED)
        lines.insert(at, PLANTED_REFUSED)
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        ccs.CENSUS = tmp

        findings, per_slice, tally = walk()
        keys = {f.key for f in findings if f.state == "GAP"}
        print("RED 1 -- THE WALK MUST FIND THE PLANTED REFUSED ROW")
        if "J 9801" in keys:
            print("  ok    the walk found the planted row and the gate refused it")
        else:
            print("  CONTROL BROKEN: the planted refused row was never found, so")
            print("  this control proves nothing about the corpus.")
            ok = False

        print("\nRED 2 -- THE CHECK MUST FAIL ON THE PLANTED CORPUS")
        # THIS NUMBER IS THE SAME PIN AS `EXPECTED_GAP_ROWS` IN
        # `tests/test_gap_rows_on_refused_addresses.py`, AND THE TWO MUST MOVE
        # TOGETHER. The control plants one offender and requires the check to
        # convict, which only happens while the planted corpus EXCEEDS what is
        # expected. Leave this behind and the control inverts silently: the
        # planted count lands exactly on the stale expectation, the check
        # PASSES, and a control that cannot convict reports itself broken --
        # which is what it did on 2026-09-21 when the pin moved 5 -> 4 here and
        # not there.
        #
        # 5 -> 4 on 2026-09-21, tracking `C88` leaving GAP for EXCLUDED-RULED.
        failed, report = run(expect_gap=4)
        if failed and any("J 9801" in line for line in report):
            print("  ok    it FAILED and it NAMED the planted row")
        elif failed:
            print("  CONTROL BROKEN: it failed but never named J 9801 -- a red")
            print("  nobody can act on.")
            ok = False
        else:
            print("  CONTROL BROKEN: it PASSED a corpus containing a planted")
            print("  offender, so it cannot fail and certifies nothing.")
            ok = False

        print("\nRED 3 -- AN ADMITTED ADDRESS MUST NOT BE CONVICTED")
        if "J 9802" in keys:
            print("  CONTROL BROKEN: the row on an ADMITTED address was convicted")
            print("  too, so the rule is not discriminating.")
            ok = False
        else:
            print("  ok    the row carrying an admitted address is cleared, so the")
            print("        rule discriminates rather than merely refusing")
    finally:
        ccs.CENSUS = real
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + ("ALL THREE REDS FIRED -- the check can convict and can clear"
                  if ok else "CONTROL BROKEN -- see above"))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--expect-gap", type=int, default=None,
                    help="fail if the distinct GAP-row count is not this")
    ap.add_argument("--demonstrate-red", action="store_true",
                    help="prove this check can fail, and can clear")
    args = ap.parse_args(argv)
    if args.demonstrate_red:
        return demonstrate_red()
    print("A GAP ROW ON A REFUSED ADDRESS IS FILED AGAINST THIS CENSUS'S OWN BAR")
    print("=" * 74)
    failed, report = run(args.expect_gap)
    for line in report:
        print(line)
    print("\n" + ("FAILED" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
