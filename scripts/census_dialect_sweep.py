"""Find every census state cell spelled in a dialect the counter cannot read.

WHY THIS EXISTS. A state cell the shipped parser could not spell used to return
the empty string, and an empty string removes the row from the NUMERATOR and
the DENOMINATOR at the same instant -- silently, with no error and no diff that
looks like a state change. Two rows lived that way through the freeze the
number 409 is taken from. `count_census_states.state_of` now REFUSES on such a
cell, which stops the NEXT one; this script answers the other half of the
question, which a refusal cannot: HOW MANY HAVE THERE EVER BEEN.

WHAT IT SWEEPS. Every markdown file under `_audit/_census/`, not only the four
counted slices -- because a file's exclusion from the count is a REASON to look
at it, not a reason to skip it. Each hit is labelled `counted=True/False` so a
reader can tell a row that left the census from a row that was never in it.
`mcp-inventory.md` runs a deliberately different vocabulary (`PROVEN-LIVE`,
`TESTED-ONLY`, `KNOWN-BROKEN`) and is expected to be clean here for a reason
worth stating: those spellings share no complete WORD SET with the census
states, so they are a different language rather than a misspelling of this one.

    ./venv/Scripts/python.exe scripts/census_dialect_sweep.py
    ./venv/Scripts/python.exe scripts/census_dialect_sweep.py --ref 1c08e5f
    ./venv/Scripts/python.exe scripts/census_dialect_sweep.py --all-history \
        --withdraw CANNOT-DELIVER

`--withdraw` IS NOT A CONVENIENCE, IT IS THE ARCHAEOLOGY. A taught spelling is
invisible to this sweep by construction, so `--all-history` on its own answers
"is anything hidden from the counter AS IT STANDS NOW" and returns 0 -- which
is true, and which was very nearly written up as "the dialect never cost
anything". Withdrawing the spelling asks the other question: what did it cost
before anyone taught it.

MEASURED 2026-09-19 with `--all-history --withdraw CANNOT-DELIVER` over the 61
commits that have ever touched the four counted slices: exactly two (file, row,
dialect) triples in the whole record -- `M M1` and `M M2`, both
`**CANNOT-DELIVER**`, both present in 11 commits from 2026-09-03 to 2026-09-05,
and `state_of` read NOTHING for them in every one. `02e617d` rewrote both cells
to the long spelling, so HEAD is clean.

THE CONTROL, AND IT MUST FIRE. `--control` withdraws `CANNOT-DELIVER` from the
vocabulary and re-sweeps the frozen commit. A sweep that reports nothing is
indistinguishable from a sweep that cannot see, and this repository has found
ten checks that could not fire in two days. The control fails the run if the
withdrawal does NOT produce the two known rows.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import count_census_states as ccs  # noqa: E402  (the shipped instrument)

ROOT = pathlib.Path(__file__).resolve().parents[1]
CENSUS_REL = "_audit/_census"
#: The two rows the dialect hid, and the only two the record has ever held.
#: Not a filter -- the control asserts the sweep RECOVERS exactly these when the
#: spelling is withdrawn, so the number can only go up by measurement.
KNOWN = {("messaging-and-content.md", "M1", "CANNOT-DELIVER"),
         ("messaging-and-content.md", "M2", "CANNOT-DELIVER")}


def _git(args: list[str]) -> str | None:
    out = subprocess.run(["git"] + args, cwd=str(ROOT), capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", errors="replace")


def census_files(ref: str | None) -> list[str]:
    if ref is None:
        return sorted(p.name for p in (ROOT / CENSUS_REL).glob("*.md"))
    listing = _git(["ls-tree", "--name-only", f"{ref}:{CENSUS_REL}"]) or ""
    return sorted(n for n in listing.split() if n.endswith(".md"))


def slice_text(name: str, ref: str | None) -> str:
    if ref is None:
        path = ROOT / CENSUS_REL / name
        return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    return _git(["show", f"{ref}:{CENSUS_REL}/{name}"]) or ""


def scan(name: str, ref: str | None):
    """Yield (name, lineno, row_id, state_or_blank, [dialects], capability)."""
    for lineno, line in enumerate(slice_text(name, ref).splitlines(), 1):
        if not line.startswith("|"):
            continue
        c = ccs.cells(line)
        if len(c) < 3:
            continue
        if c[0] and set(c[0]) <= set("-: "):
            continue
        if not ccs.ROW.match(line) or c[0].lower() in ccs.HEADERS:
            continue
        state, dialects = ccs.classify(c)
        if dialects:
            yield name, lineno, c[0], state, dialects, c[1][:70]


def sweep(ref: str | None, label: str) -> int:
    counted = set(ccs.SLICES.values())
    hits = 0
    for name in census_files(ref):
        for nm, lineno, rid, state, dialects, cap in scan(name, ref):
            hits += 1
            print(f"  {nm:26s} line {lineno:5d}  row {rid:8s}  "
                  f"counted={str(nm in counted):5s}  "
                  f"state_of={state or 'NOTHING':22s}  {'/'.join(dialects)}")
            print(f"        capability: {cap}")
    print(f"  {label}: {hits} dialect cell(s)")
    return hits


class withdrawn:
    """Take a spelling back OUT of the vocabulary for the length of a sweep.

    THIS IS THE ONLY WAY TO ASK THE ARCHAEOLOGICAL QUESTION. Once a dialect is
    taught, a sweep of history reports zero -- correct about today, useless
    about the past, and indistinguishable from a sweep that cannot see. The
    first `--all-history` run written here returned 0 for exactly that reason
    and would have been believed. So the two questions are separated: WITHOUT a
    withdrawal the sweep asks "is anything hidden from the counter as it stands
    now", WITH one it asks "what did this spelling cost before it was taught".
    """

    def __init__(self, spelling: str) -> None:
        self.spelling = spelling
        self.was_present = False

    def __enter__(self) -> "withdrawn":
        self.was_present = self.spelling in ccs.STATES
        ccs.STATES.discard(self.spelling)
        return self

    def __exit__(self, *_exc) -> None:
        if self.was_present:
            ccs.STATES.add(self.spelling)


def all_history() -> int:
    paths = [f"{CENSUS_REL}/{n}" for n in ccs.SLICES.values()]
    revs = (_git(["log", "--format=%H %ad", "--date=short", "--"] + paths) or "")
    revs = [r for r in revs.splitlines() if r.strip()]
    print(f"commits that have ever touched the four counted slices: {len(revs)}")
    seen: dict[tuple[str, str, str], list[tuple[str, str, str]]] = {}
    for rev in revs:
        sha, _, date = rev.partition(" ")
        for name in ccs.SLICES.values():
            for nm, _ln, rid, state, dialects, _cap in scan(name, sha):
                for d in dialects:
                    seen.setdefault((nm, rid, d), []).append(
                        (sha[:7], date, state or "NOTHING"))
    print(f"distinct (file, row, dialect) triples across ALL history: {len(seen)}")
    for key in sorted(seen):
        obs = seen[key]
        states = sorted({s for _a, _b, s in obs})
        print(f"  {key[0]:26s} row {key[1]:8s} {key[2]:22s} in {len(obs):3d} "
              f"commits  {obs[-1][1]}..{obs[0][1]}  state_of={states}")
    return len(seen)


def control() -> int:
    """Withdraw the taught spelling and prove the sweep can still see it."""
    spelling = "CANNOT-DELIVER"
    if spelling not in ccs.STATES:
        print(f"control: FAIL -- {spelling!r} is not in STATES, so withdrawing "
              f"it proves nothing. Has the vocabulary been edited?")
        return 1
    with withdrawn(spelling):
        found = {(nm, rid, d)
                 for name in census_files("1c08e5f")
                 for nm, _ln, rid, _st, ds, _cap in scan(name, "1c08e5f")
                 for d in ds}
    ok = found == KNOWN
    print(f"control: withdrew {spelling!r} and re-swept 1c08e5f")
    for hit in sorted(found):
        print(f"  recovered {hit}")
    print(f"control: {'PASS' if ok else 'FAIL'} -- expected {sorted(KNOWN)}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", default=None,
                    help="git ref to sweep instead of the working tree")
    ap.add_argument("--all-history", action="store_true",
                    help="sweep every commit that touched the counted slices")
    ap.add_argument("--withdraw", default="",
                    help="take a spelling back out of STATES for this sweep, "
                         "which is the only way to ask what it cost before it "
                         "was taught (e.g. --withdraw CANNOT-DELIVER)")
    ap.add_argument("--control", action="store_true",
                    help="withdraw a taught spelling and prove the sweep sees it")
    args = ap.parse_args(argv)

    fail = 0
    if args.control:
        fail |= control()

    hold = withdrawn(args.withdraw) if args.withdraw else None
    if hold is not None:
        hold.__enter__()
        if not hold.was_present:
            print(f"NOTE: {args.withdraw!r} was not in STATES to begin with, so "
                  f"this sweep is the same as one without --withdraw.")
    try:
        if args.all_history:
            all_history()
            return fail
        label = f"at {args.ref}" if args.ref else "at HEAD (working tree)"
        if args.withdraw:
            label += f" with {args.withdraw!r} withdrawn"
        print(f"sweeping {CENSUS_REL} {label}")
        hits = sweep(args.ref, label)
    finally:
        if hold is not None:
            hold.__exit__()
    return 1 if (hits or fail) else 0


if __name__ == "__main__":
    sys.exit(main())
