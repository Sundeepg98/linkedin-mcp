"""Does the blocker map agree with the ledger's published R/W SPLIT?

WHY THIS EXISTS, AND WHY IT IS A REPORT RATHER THAN A GATE.
`build_blocker_map.py` asserts on per-blocker COUNTS and on nothing else. That
leaves a whole class of disagreement unwatched: the ledger publishes an R/W
split for 88 of its 97 blockers, and a blocker can be UNDER on its total while
OVER on one direction -- in which case the count assertion is silent by
construction.

THE CLASS IS NOT THEORETICAL AND THE REASON IS STRUCTURAL. A row RE-FILED from
one blocker to another is COUNT-NEUTRAL across the pair, so no count assertion
anywhere can see it; but it MOVES THE SPLIT of both. `SEARCH-RESULTS-SURFACE`'s
own assignment note says so in writing -- *"the split is not claimed for the
post-freeze set ... That is what a re-file does"*. So the split is the only
signal that distinguishes the two things a PARTIAL blocker can mean:

    a published row was LOST, nobody can say which        -> a real hole
    a published row was RE-FILED OUT and this map HAS it  -> not a hole at all

**AMENDED 2026-09-20 -- THOSE ARE TWO CAUSES AND THERE ARE THREE.** Both of the
lines above describe movement AFTER publication. The third is an error AT
publication: the published cell was never a count. `NEWSLETTER-SURFACE` is that
case and it was convicted on a supply argument, not on a subset argument -- the
whole newsletter family in the frozen 409 holds TEN writes and the cell
published ELEVEN, so no choice of twelve rows, no re-file and no lost row could
ever have produced it. See `_audit/2026-09-20-the-split-ruling.md`, and
`_audit/2026-09-19-the-remaining-partials.md` section 5.4, which found it first.

THE DISCRIMINATOR IS A SUBTRACTION AND IT ALREADY SHIPPED, one file away.
`_check_refile_destination_credit.publishers()` knows which rows arrived from
somewhere else. Subtract their directions from `held` and the causes come
apart, so this file IMPORTS that rather than re-deriving it:

    RE-FILED-IN   the over-run vanishes once incoming rows are subtracted
    LOST          the blocker is UNDER on its own count; rows are missing
    AT-BIRTH      COMPLETE on count, nothing incoming, and still over --
                  nothing moved and nothing is missing, so the only thing
                  left that can be wrong is the published figure

Measured 2026-09-19 on `424fe66`, this reports 2 blockers over-published on a
direction, both COMPLETE on their counts and therefore invisible to the shipped
builder. A third (`COMPANY-PAGE-SURFACE`, 14R held against 13R published) is
NOT reported here and the limitation is stated rather than hidden: `jobs.md`
keys direction by RANGE (`106-114`) and not by row id, so this script cannot
read the direction of a `J` row and SKIPS any blocker holding one. It reports
how many it skipped for that reason.

IT IS DELIBERATELY NOT AN ASSERTION. Two of the three known over-runs are
documented and were ruled deliberate, so a red gate here would fail CI on work
somebody decided. The rule this supports is narrower: a NEW over-run must be
argued. Promote to an assertion only once the known three are adjudicated.

    **CORRECTED 2026-09-20, and the paragraph above keeps its text because the
    POLICY it sets is still right.** The count was wrong: for
    `NEWSLETTER-SURFACE` no committed source ever ruled that over-run
    deliberate. The only document that discussed it ruled the OPPOSITE -- that
    the published split is unsatisfiable -- and this file went on reporting it
    as one of a pair somebody had decided. One of the three was ruled
    deliberate, not two, and that cell has since been corrected in the ledger.
    A justification for not gating is exactly the sentence nobody re-reads.

CONTROLS, because a check that cannot fail certifies nothing. `--control`
injects a synthetic over-run into the tally and requires the report to name it.
`--control-causes` injects ONE over-run of EACH cause, into blockers the real
data does not report, and requires each to be classified correctly -- a
classifier that answers the same word every time passes the first control and
fails this one.

    ./venv/Scripts/python.exe scripts/_check_published_split.py
    ./venv/Scripts/python.exe scripts/_check_published_split.py --control
    ./venv/Scripts/python.exe scripts/_check_published_split.py --control-causes
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_blocker_map as bbm  # noqa: E402
#: IMPORTED, NEVER RE-DERIVED. `publishers()` is the committed answer to "which
#: rows arrived here from somewhere else", and this file needs exactly that to
#: tell an incoming re-file from a cell that was wrong when it was written.
#: Four waves reimplemented a shipped instrument on 2026-09-05 and three got a
#: broken one; the standing rule is IMPORT IT.
import _check_refile_destination_credit as rdc  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
CENSUS = ROOT / "_audit" / "_census"

#: 0-based index of the R/W cell in each slice's row table. `jobs.md` has none
#: -- see the module docstring.
SLICE_DIR_COL = {
    "M": ("messaging-and-content.md", 4),
    "N": ("network.md", 2),
    "P": ("profile.md", 2),
}
ROW_ID = re.compile(r"[A-Z]{0,2}\d{1,3}")
DIR_CELLS = {"R", "W", "R+W", "RW", "R/W"}
RANKED_HEADER = "| # | blocker | rows | R/W | boundary | ruling | cost |"


def _norm(d: str) -> str:
    return "RW" if d in ("R+W", "RW", "R/W") else d


def row_directions() -> dict[str, str]:
    """{slice-qualified row id: 'R' | 'W' | 'RW'} read off the census tables."""
    out: dict[str, str] = {}
    for letter, (name, col) in SLICE_DIR_COL.items():
        text = (CENSUS / name).read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) <= col:
                continue
            rid = cells[0].strip("`* ")
            if not ROW_ID.fullmatch(rid):
                continue
            d = cells[col].strip("`* ")
            if d in DIR_CELLS:
                out.setdefault(letter + " " + rid, _norm(d))
    return out


def published_splits() -> dict[str, dict[str, int]]:
    """The ledger's per-blocker R/W split, parsed from its ranked table.

    Located by HEADER ROW for the same reason `build_blocker_map` does it that
    way: another wave appending to the ledger slides every table down, and a
    reading pinned to a line offset is the defect that already fired once.
    """
    lines = bbm.LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
    out: dict[str, dict[str, int]] = {}
    for row in bbm._table_after(lines, RANKED_HEADER):
        m = re.match(r"^\|\s*\d+\s*\|\s*`([A-Z0-9-]+)`\s*\|\s*\d+\s*\|([^|]*)\|", row)
        if not m:
            continue
        spec = {"R": 0, "W": 0, "RW": 0}
        for n, kind in re.findall(r"(\d*)\s*(RW|R\+W|R|W)", m.group(2)):
            spec[_norm(kind)] += int(n) if n else 1
        if any(spec.values()):
            out[m.group(1)] = spec
    return out


DIRS = ("R", "W", "RW")


def classify_overrun(pub: dict[str, int], held: dict[str, int],
                     own: dict[str, int]) -> tuple[str, str]:
    """Which of the three causes explains this blocker's direction over-run?

    `own` is `held` with every INCOMING re-filed row subtracted, so the three
    branches are asked in the order a cause can be RULED OUT, not in the order
    they are interesting:

    1. subtract the arrivals. If nothing is over any more, the surplus WAS the
       arrivals and there is no defect in the published cell at all.
    2. if the blocker's own rows do not even reach its published total, rows
       are MISSING, and a direction can read over simply because the rows that
       went missing were the other direction. The hole is the finding.
    3. otherwise the map holds exactly what was published, all of it the
       blocker's own, and the split still disagrees. Nothing moved and nothing
       is missing. THE PUBLISHED FIGURE IS THE ONLY THING LEFT THAT CAN BE
       WRONG -- and this branch is why the docstring's two causes were two
       short of three.

    A blocker holding MORE rows than it published cannot reach here: the
    builder's own over-count assertion is red before this file runs. It is
    named anyway rather than folded into branch 3, because silently calling an
    over-count an at-birth error would be this file inventing a verdict.
    """
    still = [k for k in DIRS if own[k] > pub[k]]
    if not still:
        return "RE-FILED-IN", ("the surplus is rows that ARRIVED here on a "
                               "committed re-file; the published cell is not "
                               "implicated")
    own_total = sum(own[k] for k in DIRS)
    pub_total = sum(pub[k] for k in DIRS)
    if own_total < pub_total:
        return "LOST", (f"own rows {own_total} against a published {pub_total}"
                        f" -- rows are missing, and the direction reads over "
                        f"because the missing ones were not {','.join(still)}")
    if own_total > pub_total:
        return "OVER-COUNT", (f"own rows {own_total} EXCEED the published "
                              f"{pub_total}; the builder's count assertion "
                              f"should already be red")
    return "AT-BIRTH", ("count COMPLETE, nothing incoming, still over -- "
                        "nothing moved and nothing is missing, so the "
                        "published cell was wrong when it was written")


def _tally(assign, dirs) -> dict[str, dict[str, int]]:
    held: dict[str, dict[str, int]] = {}
    for rid, (blocker, *_rest) in assign.items():
        k = dirs.get(rid, "?")
        held.setdefault(blocker, {"R": 0, "W": 0, "RW": 0, "?": 0})
        held[blocker][k] = held[blocker].get(k, 0) + 1
    return held


def _incoming(dirs) -> dict[str, dict[str, int]]:
    """{destination blocker: {direction: count}} for every RE_FILED arrival."""
    out: dict[str, dict[str, int]] = {}
    for rid, (_src, dest) in rdc.publishers().items():
        d = dirs.get(rid, "?")
        out.setdefault(dest, {"R": 0, "W": 0, "RW": 0, "?": 0})
        out[dest][d] = out[dest].get(d, 0) + 1
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--control", action="store_true",
                    help="inject a synthetic over-run and require it be named")
    ap.add_argument("--control-causes", action="store_true",
                    help="inject one over-run of EACH cause and require each "
                         "to be classified correctly")
    args = ap.parse_args(argv)

    dirs = row_directions()
    _gap, _cur, assign, _problems = bbm.build()
    published = published_splits()

    held = _tally(assign, dirs)
    incoming = _incoming(dirs)

    if args.control:
        victim = sorted(published)[0]
        held.setdefault(victim, {"R": 0, "W": 0, "RW": 0, "?": 0})
        held[victim]["R"] = published[victim]["R"] + 99
        held[victim]["?"] = 0

    want: dict[str, str] = {}
    if args.control_causes:
        want = _inject_causes(published, held, incoming)

    print(f"blockers with a published split   {len(published)}")
    over: list[str] = []
    got: dict[str, str] = {}
    skipped = 0
    for b in sorted(published):
        h = held.get(b)
        if not h:
            continue
        if h["?"]:
            skipped += 1
            continue
        bad = [k for k in DIRS if h[k] > published[b][k]]
        if not bad:
            continue
        over.append(b)
        inc = incoming.get(b, {"R": 0, "W": 0, "RW": 0, "?": 0})
        own = {k: h[k] - inc.get(k, 0) for k in DIRS}
        cause, why = classify_overrun(published[b], h, own)
        got[b] = cause
        print(f"  OVER on {','.join(bad):<3s}  {b:30s} "
              f"published R{published[b]['R']} W{published[b]['W']} "
              f"RW{published[b]['RW']}   "
              f"held R{h['R']} W{h['W']} RW{h['RW']}")
        print(f"      incoming R{inc['R']} W{inc['W']} RW{inc['RW']}   "
              f"own R{own['R']} W{own['W']} RW{own['RW']}")
        print(f"      CAUSE {cause} -- {why}")
    print(f"blockers OVER on some direction   {len(over)}")
    print(f"blockers SKIPPED (a held row's direction is unreadable -- the "
          f"jobs-slice limitation in the docstring)   {skipped}")

    if args.control:
        victim = sorted(published)[0]
        ok = victim in over
        print(f"\ncontrol: injected over-run on {victim} -- "
              f"{'NAMED, the report can fail' if ok else 'NOT NAMED -- BROKEN'}")
        return 0 if ok else 1

    if args.control_causes:
        bad = 0
        print("")
        #: THE DERIVATION-LIVENESS HALF, AND IT WAS ADDED BECAUSE THIS CONTROL
        #: WAS SHOWN PASSING WITHOUT IT. Stub `_incoming()` to return nothing
        #: -- the exact defect of re-deriving instead of importing
        #: `publishers()` -- and the three injected cases still classified
        #: correctly, because the RE-FILED-IN injection plants its own arrival
        #: and never touches the real derivation. Meanwhile the real report in
        #: the same run called `SEARCH-RESULTS-SURFACE` AT-BIRTH, which is the
        #: verdict this whole classifier exists to reserve for a cell that was
        #: wrong when it was written. A control that exercises the LOGIC and
        #: not the INPUT certifies an instrument that is already lying.
        arrivals = sum(v[k] for v in _incoming(dirs).values()
                       for k in ("R", "W", "RW", "?"))
        expected = len(rdc.publishers())
        live = arrivals == expected and arrivals > 0
        print(f"control-causes: arrivals derived from publishers() {arrivals} "
              f"against {expected} RE_FILED rows -- "
              f"{'LIVE' if live else 'DEAD, the subtraction reaches nothing'}")
        if not live:
            bad += 1
        for b in sorted(want):
            actual = got.get(b, "NOT REPORTED AT ALL")
            ok = actual == want[b]
            bad += 0 if ok else 1
            print(f"control-causes: {b:30s} injected {want[b]:12s} "
                  f"classified {actual:12s} {'OK' if ok else 'WRONG'}")
        print(f"control-causes: {bad} failure(s)")
        return 1 if bad else 0
    return 0


#: THE VICTIMS ARE CHOSEN, NOT NAMED, and the choice is ASSERTED clean first.
#: Register entry 21.1 records the exact way this control fails silently: its
#: first version injected into a blocker the report ALREADY named, so it passed
#: whether or not the injection did anything -- it was measuring the baseline.
#: Here the stakes are higher, because a class-specific control injected into a
#: blocker that is already over would compare the injected class against the
#: REAL one and read as a misclassification, which is the same defect wearing
#: the opposite sign.
def _inject_causes(published, held, incoming) -> dict[str, str]:
    """Plant one over-run of each cause. Returns {blocker: expected cause}."""
    clean = [b for b in sorted(published)
             if b in held and not held[b]["?"]
             and not any(held[b][k] > published[b][k] for k in DIRS)
             and b not in incoming
             and published[b]["W"] >= 2 and held[b]["W"] >= 2]
    if len(clean) < 3:
        raise SystemExit(
            "control-causes: fewer than three clean victims "
            f"({len(clean)}); injecting into a blocker the report already "
            "names would measure the baseline, not the instrument")
    a, b, c = clean[0], clean[1], clean[2]

    # RE-FILED-IN: a read ARRIVES. held goes up, own does not.
    held[a]["R"] += 1
    incoming.setdefault(a, {"R": 0, "W": 0, "RW": 0, "?": 0})
    incoming[a]["R"] += 1

    # LOST: one write turns into a read AND one more write goes missing, so the
    # direction reads over while the count falls short.
    held[b]["R"] += 1
    held[b]["W"] -= 2

    # AT-BIRTH: one write reads as a read. Count unmoved, nothing incoming.
    # This is the real `NEWSLETTER-SURFACE` shape.
    held[c]["R"] += 1
    held[c]["W"] -= 1
    return {a: "RE-FILED-IN", b: "LOST", c: "AT-BIRTH"}


if __name__ == "__main__":
    sys.exit(main())
