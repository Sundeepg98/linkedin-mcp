"""Measure the POSITIONAL POINTER GRAPH in `_audit/_census/`, and plant rows to move it.

WHAT THIS IS FOR. `_audit/2026-09-20-the-reason-kinds.md` found that 127 of 309
write-off reason cells are not reasons but POINTERS, and that the worst dialect is
the bare word `same`, which resolves BY POSITION to the nearest substantive row
above it in the same table. Nothing marks a row as load-bearing for the rows beneath
it. A row inserted into the middle of a table therefore re-points every dependent
below it and changes their classification -- with no edit to those rows, no error and
no warning. That document proved the shape at one point (its harness M7). THIS FILE
measures the whole graph and then plants a row at EVERY exposed slot, because one
example proves the mechanism exists and a sweep measures how much of the census
stands on it.

IT IMPORTS THE SHIPPED PARSE AND ADDS NONE OF ITS OWN. `walk`, `BACKREF`,
`is_substantive` and the table segmentation all come from
`classify_writeoff_reasons`, which imports `enumerate_gap_rows`, which imports
`count_census_states`. Four waves reimplemented that parse in one day and three got a
broken one. The consequence is stated rather than hidden: this file inherits those
blind spots exactly -- a row whose state cell is prose is invisible here too.

THE THREE NUMBERS THIS PRODUCES, and what each one means.

  POINTER CELLS      how many cells say `same` and resolve by position. Counted over
                     ALL stated rows, not only write-offs, because `same` points at
                     the row above whatever state that row is in -- a filter applied
                     before resolution breaks exactly the chains being measured.
  READ DISTANCE      how far a HUMAN must walk up to reach the argument. The resolver
                     jumps straight past intervening `same` rows to the first
                     substantive one, so the resolver's depth is always 1 and says
                     nothing about the corpus. A reader's is not.
  EXPOSED SLOTS      the actual fragility. For a dependent at table position p whose
                     donor sits at d, ANY substantive non-pointer row inserted at a
                     position in (d, p] becomes the new donor. That is p-d distinct
                     insertion points per dependent. The union over all dependents is
                     the number of places in this census where adding one row silently
                     re-argues a row somebody else wrote.

    python scripts/measure_pointer_graph.py
    python scripts/measure_pointer_graph.py --edges
    python scripts/measure_pointer_graph.py --plant "P D15"
    python scripts/measure_pointer_graph.py --plant-sweep

`--plant` and `--plant-sweep` NEVER WRITE INTO THE REPO. They copy the tree into a
sandbox, mutate the copy, run the real scripts there as subprocesses, and compare.
`linkedin_server/` is not touched even briefly: several agents write that package
concurrently and `_audit/INSTRUMENTS.md` already records a wave that mutated it in the
live tree and had to be ruled against.

EVERY RUN GETS A SANDBOX OF ITS OWN. Unless `--sandbox` names a path, `--plant`,
`--plant-sweep` and `--selftest` each make a fresh directory under the system temp
directory (`pointer-graph-sandbox-*` / `pointer-graph-selftest-*`), build the tree one
level inside it -- so the two TSVs a plant writes beside the tree land in that run's
directory too, not in the shared temp root -- and remove it when the run ends, passed
or failed. It used to be one fixed path, and two concurrent runs deleted each other's
sandbox mid-check. A `--sandbox` path is the caller's: wiped and rebuilt before use,
and left in place afterwards.

WHAT A PLANT PROVES, STATED SO IT CAN BE ARGUED WITH. It is not a defect in the
classifier and the classifier is not what is on trial. `same` means "the row above",
the classifier implements that faithfully, and the fragility is the NOTATION. The
receipt is the pair of facts together: a dependent's verdict changed, AND no
instrument in this repo said anything about that dependent.
"""
from __future__ import annotations

import argparse
import collections
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import count_census_states as ccs  # noqa: E402
import classify_writeoff_reasons as cwr  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: The reason cell given to a planted row. Chosen so its verdict is a SINGLE kind and
#: not one a real donor in this corpus is likely to carry, which is what makes a
#: dependent's inherited verdict visibly change rather than merely possibly change.
#: It fires exactly two WORLD-FACT signals (`mobile-only`, `http-404`) and nothing
#: else; `--plant` asserts that before drawing any conclusion, because a planted row
#: whose kind matched the donor's would produce a GREEN sweep for the wrong reason.
PLANT_REASON = "PLANTED CONTROL -- mobile only, and the surface is 404"
PLANT_ID = "PLANT1"
PLANT_KIND = "WORLD-FACT"


class Edge:
    """One positional pointer: `dep` reads its argument off `donor`, by position."""

    __slots__ = ("dep", "donor", "dep_pos", "donor_pos", "table_key")

    def __init__(self, dep, donor, dep_pos, donor_pos, table_key):
        self.dep, self.donor = dep, donor
        self.dep_pos, self.donor_pos = dep_pos, donor_pos
        self.table_key = table_key

    @property
    def read_distance(self) -> int:
        """Rows a HUMAN walks up from the pointer before the argument appears."""
        return self.dep_pos - self.donor_pos

    @property
    def slots(self) -> list[tuple[str, int]]:
        """Every insertion position that would re-point this dependent.

        A row inserted at table index `i` lands before the row currently at `i`. For
        the planted row to sit between donor and dependent, `i` must be in
        (donor_pos, dep_pos] -- `read_distance` distinct positions.
        """
        return [(self.table_key, i)
                for i in range(self.donor_pos + 1, self.dep_pos + 1)]


def build_graph(ref: str | None = None):
    """(all rows, edges, orphan pointers, table index).

    ORPHANS ARE RETURNED RATHER THAN DROPPED. A cell that says `same` with no
    substantive row above it in its table is a pointer into nothing, and reporting
    only the edges that resolved would be a refusal that names what it did not match.
    """
    rows, dialects, stated = cwr.walk(ref)
    by_table: dict[str, list] = collections.defaultdict(list)
    for r in rows:
        by_table[r.table_key].append(r)

    edges: list[Edge] = []
    orphans: list = []
    for tkey, sib in by_table.items():
        for pos, r in enumerate(sib):
            if not cwr.BACKREF.match(r.reason):
                continue
            donor = donor_pos = None
            for i in range(pos - 1, -1, -1):
                prev = sib[i]
                if cwr.is_substantive(prev.reason) and not cwr.BACKREF.match(prev.reason):
                    donor, donor_pos = prev, i
                    break
            if donor is None:
                orphans.append(r)
            else:
                edges.append(Edge(r, donor, pos, donor_pos, tkey))
    return rows, edges, orphans, by_table, dialects, stated


# --------------------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------------------
def report(ref: str | None = None, show_edges: bool = False) -> int:
    rows, edges, orphans, by_table, dialects, stated = build_graph(ref)
    wo_states = cwr.WRITEOFF

    print("THE POSITIONAL POINTER GRAPH -- measured at "
          f"{ref or 'the working tree'}")
    print("=" * 92)
    print(f"stated rows walked           : {len(rows)}  "
          f"({', '.join(f'{k}={v}' for k, v in stated.items())})")
    print(f"tables segmented             : {len(by_table)}")
    print(f"POSITIONAL POINTER CELLS     : {len(edges) + len(orphans)}  "
          f"({len(edges)} resolve to a donor, {len(orphans)} point at nothing)")
    print()

    # -- per slice, and per state, because a union count hides which file carries it --
    per_slice = collections.Counter(e.dep.letter for e in edges)
    print(f"{'slice':30s} {'stated':>7s} {'pointers':>9s} {'write-off':>10s} "
          f"{'other state':>12s}")
    for letter, name in ccs.SLICES.items():
        sub = [e for e in edges if e.dep.letter == letter]
        wo = sum(1 for e in sub if e.dep.state in wo_states)
        print(f"{name:30s} {stated[letter]:>7d} {per_slice[letter]:>9d} "
              f"{wo:>10d} {len(sub) - wo:>12d}")
    wo_all = sum(1 for e in edges if e.dep.state in wo_states)
    print("-" * 74)
    print(f"{'TOTAL':30s} {sum(stated.values()):>7d} {len(edges):>9d} "
          f"{wo_all:>10d} {len(edges) - wo_all:>12d}")
    print()

    print("pointer cells by the STATE of the dependent row:")
    for st, n in collections.Counter(e.dep.state for e in edges).most_common():
        print(f"  {st:28s} {n:4d}   "
              f"{'WRITE-OFF' if st in wo_states else ''}")
    print()

    print("the EXACT SPELLINGS in the pointer cells, because a dialect nobody printed")
    print("is a dialect nobody can argue with:")
    for text, n in collections.Counter(e.dep.reason for e in edges).most_common():
        print(f"  {n:4d}  {text!r}")
    if orphans:
        print("  -- pointing at nothing --")
        for r in orphans:
            print(f"        {r.key} ({ccs.SLICES[r.letter]} line {r.lineno}) {r.reason!r}")
    print()

    # -- fan-out: how many rows one donor is carrying --------------------------------
    fan: dict[str, list[Edge]] = collections.defaultdict(list)
    for e in edges:
        fan[e.donor.key].append(e)
    print(f"DONORS                       : {len(fan)} rows carry the argument for "
          f"{len(edges)} others")
    hist = collections.Counter(len(v) for v in fan.values())
    for n in sorted(hist):
        print(f"  donors with {n} dependent(s) : {hist[n]:3d}")
    worst = sorted(fan.items(), key=lambda kv: -len(kv[1]))[:6]
    print("  heaviest donors:")
    for key, deps in worst:
        print(f"    {key:10s} carries {len(deps)}: "
              f"{', '.join(e.dep.key for e in deps)}")
    print()

    # -- read distance: the chain a HUMAN walks --------------------------------------
    dists = collections.Counter(e.read_distance for e in edges)
    print("READ DISTANCE -- rows a human walks up before the argument appears.")
    print("The resolver jumps straight to the donor, so its depth is always 1 and")
    print("measures nothing. This is the number that describes the corpus.")
    for d in sorted(dists):
        print(f"  {d:2d} row(s) up : {dists[d]:3d}")
    longest = max(edges, key=lambda e: e.read_distance)
    chain = by_table[longest.table_key][longest.donor_pos:longest.dep_pos + 1]
    print(f"  LONGEST: {longest.dep.key} reaches its argument "
          f"{longest.read_distance} rows up, at {longest.donor.key}")
    print("    the walk, top to bottom:")
    for r in chain:
        mark = "ARGUMENT" if r is longest.donor else (
            "pointer " if cwr.BACKREF.match(r.reason) else "other   ")
        print(f"      {mark} {r.key:10s} {r.reason[:58]!r}")
    print()

    # -- the fragility itself --------------------------------------------------------
    slot_hits: dict[tuple[str, int], list[Edge]] = collections.defaultdict(list)
    for e in edges:
        for s in e.slots:
            slot_hits[s].append(e)
    print("EXPOSED SLOTS -- insertion points that silently re-point at least one row.")
    print(f"  distinct exposed slots     : {len(slot_hits)}")
    print(f"  (slot, dependent) pairs    : {sum(len(v) for v in slot_hits.values())}")
    blast = collections.Counter(len(v) for v in slot_hits.values())
    for n in sorted(blast, reverse=True):
        print(f"  slots re-pointing {n} row(s) : {blast[n]:3d}")
    top = sorted(slot_hits.items(), key=lambda kv: -len(kv[1]))[:5]
    print("  worst single insertion points:")
    for (tkey, i), hit in top:
        sib = by_table[tkey]
        anchor = sib[i] if i < len(sib) else sib[-1]
        print(f"    before {anchor.key:10s} ({ccs.SLICES[anchor.letter]} line "
              f"{anchor.lineno}) re-points {len(hit)}: "
              f"{', '.join(e.dep.key for e in hit)}")
    print()

    if show_edges:
        print("EVERY EDGE")
        print(f"{'dependent':12s} {'donor':12s} {'up':>3s} {'state':24s} slice:line")
        for e in sorted(edges, key=lambda e: (e.dep.letter, e.dep.lineno)):
            print(f"{e.dep.key:12s} {e.donor.key:12s} {e.read_distance:>3d} "
                  f"{e.dep.state:24s} {ccs.SLICES[e.dep.letter]}:{e.dep.lineno}")
    return 0


# --------------------------------------------------------------------------------------
# The planted-row control
# --------------------------------------------------------------------------------------
def make_sandbox(dest: pathlib.Path) -> pathlib.Path:
    """A throwaway copy of the tracked tree. NOTHING in the repo is written.

    `git archive` is used rather than a directory walk so the copy is exactly the
    committed tree: an uncommitted edit of mine cannot leak into a measurement.
    """
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    tar = subprocess.run(["git", "archive", "HEAD"], cwd=str(ROOT),
                         capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", dest.as_posix()], input=tar.stdout, check=True)
    return dest


def plant_line(row, template_cells: list[str], reason: str = PLANT_REASON) -> str:
    """A table line shaped like its neighbours, carrying a substantive reason.

    The state cell is COPIED from the anchor row so the planted row is a stated row
    in the same table with the same shape. That is deliberate: it means the row
    counters DO see it (+1 in that state) while nothing sees what it did to the rows
    beneath it, which is the whole point of the control.
    """
    cells = list(template_cells)
    cells[0] = PLANT_ID
    if len(cells) > 1:
        cells[1] = "PLANTED CONTROL ROW"
    # the last non-empty cell after the state is where `split_reason` looks
    state_at = -1
    for i, cell in enumerate(cells):
        if i == 0:
            continue
        bare = cell.replace("`", "").replace("*", "").strip()
        if bare.split(" ")[0] in ccs.STATES:
            state_at = i
            break
    if state_at < 0 or state_at == len(cells) - 1:
        return ""          # no room for a reason: this anchor cannot host a plant
    cells[-1] = reason
    for i in range(state_at + 1, len(cells) - 1):
        cells[i] = ""
    return "| " + " | ".join(cells) + " |"


def classify_tsv(tree: pathlib.Path, out: pathlib.Path) -> None:
    env = dict(os.environ)
    # `build_blocker_map` and `enumerate_gap_rows` reach a frozen commit with
    # `git show`, and the sandbox is not a work tree. Point git at the real object
    # database: every call in these scripts is READ-ONLY (`git show`), so no index
    # and no ref in this repository can be written by a sandbox run.
    env["GIT_DIR"] = str(gitdir())
    subprocess.run([sys.executable, str(tree / "scripts" / "classify_writeoff_reasons.py"),
                    "--tsv", str(out)],
                   check=True, capture_output=True, env=env)


def gitdir() -> pathlib.Path:
    out = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=str(ROOT),
                         capture_output=True, check=True)
    return pathlib.Path(out.stdout.decode().strip())


#: THE OTHER HALF OF THE RECEIPT. A verdict that changed is only half the finding; the
#: other half is that NOTHING SAID SO. These are the two instruments the census is read
#: through, and a plant must be run past both -- otherwise the claim "silently" rests on
#: my not having looked.
CENSUS_INSTRUMENTS = (
    ("count_census_states.py", ["--unstated"]),
    ("build_blocker_map.py", ["--check"]),
)


def run_instruments(tree: pathlib.Path) -> dict[str, str]:
    env = dict(os.environ)
    env["GIT_DIR"] = str(gitdir())
    out = {}
    for name, extra in CENSUS_INSTRUMENTS:
        p = subprocess.run([sys.executable, str(tree / "scripts" / name), *extra],
                           capture_output=True, env=env)
        out[name] = (p.stdout.decode("utf-8", errors="replace")
                     + p.stderr.decode("utf-8", errors="replace"))
    return out


def instrument_delta(before: dict[str, str], after: dict[str, str],
                     victims: list[str]) -> None:
    """Print what each census instrument said about a plant, and about its victims.

    NAMES WHAT IT SAW, not only what it failed to match. A line that says "0 mentions"
    and nothing else cannot be told from an instrument that was never run.
    """
    import difflib
    for name, _extra in CENSUS_INSTRUMENTS:
        b = before[name].splitlines()
        a = after[name].splitlines()
        delta = [ln for ln in difflib.unified_diff(b, a, lineterm="", n=0)
                 if ln[:1] in "+-" and ln[:3] not in ("+++", "---")]
        print(f"  {name}")
        if not delta:
            print("      output BYTE-IDENTICAL -- it did not notice the planted row "
                  "at all")
        else:
            print(f"      {len(delta)} line(s) changed, every one of them below:")
            for ln in delta:
                print(f"        {ln}")
        hits = [ln for ln in a
                if any(v in ln for v in victims)]
        print(f"      lines mentioning the re-pointed rows ({', '.join(victims)}): "
              f"{len(hits)}")
        for ln in hits:
            print(f"        {ln.strip()}")


#: Columns compared between a clean run and a planted run. `line` is excluded because
#: every row below an insertion shifts by one and that is not a change in meaning; it
#: is excluded EXPLICITLY rather than quietly, so a reader can object to it.
COMPARED = ("state", "kind", "contingent", "has_reopener", "has_reason_cell",
            "source", "resolution", "signals", "reason")


def read_tsv(path: pathlib.Path) -> dict[str, dict[str, str]]:
    lines = path.read_text(encoding="ascii", errors="replace").splitlines()
    head = lines[0].split("\t")
    out = {}
    for line in lines[1:]:
        c = line.split("\t")
        rec = dict(zip(head, c))
        out[rec["row"]] = rec
    return out


def diff_rows(before: dict, after: dict) -> tuple[list, list, list]:
    """(rows whose compared fields moved, rows that vanished, rows that appeared)."""
    moved = []
    for key, b in before.items():
        a = after.get(key)
        if a is None:
            continue
        delta = {f: (b.get(f), a.get(f)) for f in COMPARED if b.get(f) != a.get(f)}
        if delta:
            moved.append((key, delta))
    gone = [k for k in before if k not in after]
    new = [k for k in after if k not in before]
    return moved, gone, new


def plant(target: str | None, sweep: bool, sandbox: pathlib.Path,
          reason: str = PLANT_REASON) -> int:
    rows, edges, orphans, by_table, _dialects, _stated = build_graph(None)
    if not edges:
        print("REFUSED: this census holds no positional pointer at all. That is either "
              "the fix having\nlanded -- in which case delete this instrument -- or a "
              "parse that stopped seeing them. It is\nNOT reported as a clean sweep.")
        return 1
    tree = make_sandbox(sandbox)
    base_tsv = sandbox.parent / "plant-base.tsv"
    classify_tsv(tree, base_tsv)
    before = read_tsv(base_tsv)
    inst_before = {} if sweep else run_instruments(tree)

    slot_hits: dict[tuple[str, int], list[Edge]] = collections.defaultdict(list)
    for e in edges:
        for s in e.slots:
            slot_hits[s].append(e)

    if sweep:
        todo = sorted(slot_hits.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    else:
        want = [e for e in edges if e.dep.key == (target or "").strip()]
        if not want:
            print(f"no positional pointer row with key {target!r}. "
                  f"Pointer rows are: {', '.join(sorted(e.dep.key for e in edges))}")
            return 1
        e = want[0]
        key = (e.table_key, e.dep_pos)          # plant directly above the dependent
        todo = [(key, slot_hits[key])]

    print("THE PLANTED-ROW CONTROL")
    print("=" * 92)
    print(f"sandbox                      : {tree}")
    print(f"clean write-off rows         : {len(before)}")
    print(f"slots to plant               : {len(todo)}")
    print(f"planted reason               : {reason!r}")
    print()

    totals = collections.Counter()
    silent_rows: set[str] = set()
    detail: list[str] = []
    for (tkey, idx), hit in todo:
        sib = by_table[tkey]
        anchor = sib[idx] if idx < len(sib) else sib[-1]
        name = ccs.SLICES[anchor.letter]
        src = (ROOT / "_audit" / "_census" / name)
        raw = src.read_bytes().decode("utf-8", errors="replace")
        # CRLF is preserved by splitting on the line boundary and re-joining with the
        # file's own terminator: a harness that silently rewrites line endings makes
        # every diff unreadable, which is a defect a sibling wave already paid for.
        nl = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(nl)
        anchor_line = anchor.lineno - 1
        template = ccs.cells(lines[anchor_line])
        planted = plant_line(anchor, template, reason)
        if not planted:
            totals["unplantable"] += 1
            detail.append(f"  SKIPPED before {anchor.key}: its table has no cell after "
                          f"the state, so a planted row could carry no reason")
            continue
        lines.insert(anchor_line, planted)
        (tree / "_audit" / "_census" / name).write_bytes(nl.join(lines).encode("utf-8"))
        after_tsv = sandbox.parent / "plant-after.tsv"
        classify_tsv(tree, after_tsv)
        after = read_tsv(after_tsv)
        # restore before drawing any conclusion, so a crash cannot leave the sandbox
        # carrying a mutation into the next slot
        (tree / "_audit" / "_census" / name).write_bytes(raw.encode("utf-8"))

        moved, gone, new = diff_rows(before, after)
        moved = [(k, d) for k, d in moved if k != f"{anchor.letter} {PLANT_ID}"]
        kindmoved = [(k, d) for k, d in moved if "kind" in d]

        # THE SILENCE, MEASURED RATHER THAN ASSERTED. Only on a single plant: running
        # the blocker map 71 times says nothing the first run does not.
        if not sweep:
            (tree / "_audit" / "_census" / name).write_bytes(
                nl.join(lines).encode("utf-8"))
            inst_after = run_instruments(tree)
            (tree / "_audit" / "_census" / name).write_bytes(raw.encode("utf-8"))
            print("  WHAT THE TWO CENSUS INSTRUMENTS SAID ABOUT IT:")
            instrument_delta(inst_before, inst_after,
                             [k for k, _ in kindmoved] or [e.dep.key for e in hit])
            print()
        totals["slots"] += 1
        totals["slots_that_moved_a_kind"] += 1 if kindmoved else 0
        totals["row_kind_changes"] += len(kindmoved)
        for k, _d in kindmoved:
            silent_rows.add(k)
        if not sweep or kindmoved:
            detail.append(
                f"  plant before {anchor.key:10s} ({name} line {anchor.lineno}) "
                f"-> predicted {len(hit)} re-pointed, MEASURED "
                f"{len(kindmoved)} verdict change(s)")
            for k, d in kindmoved:
                bits = "; ".join(f"{f}: {bv!r} -> {av!r}"
                                 for f, (bv, av) in sorted(d.items())
                                 if f in ("kind", "resolution", "source"))
                detail.append(f"      {k:10s} {bits}")

    for line in detail:
        print(line)
    print()
    print(f"slots planted                        : {totals['slots']}")
    print(f"slots that changed another row's KIND : "
          f"{totals['slots_that_moved_a_kind']}")
    print(f"(slot, row) verdict changes           : {totals['row_kind_changes']}")
    print(f"DISTINCT ROWS whose verdict can be changed by an edit that never touches "
          f"them: {len(silent_rows)}")
    if silent_rows:
        print("  " + ", ".join(sorted(silent_rows)))
    if totals["unplantable"]:
        print(f"anchors that could not host a plant   : {totals['unplantable']} "
              f"(reported above, not silently dropped)")

    # THIS SWEEP UNDERCOUNTS AND SAYS BY HOW MUCH. The classifier publishes a verdict
    # only for WRITE-OFF rows, so a pointer row sitting at GAP or COVERED-PROVEN is
    # re-pointed by exactly the same mechanism and produces no diff here -- not because
    # nothing happened to it, but because no artifact ever stated its verdict. A number
    # whose blind spot is not published is a number on its way to being a quotation.
    invisible = [e.dep for e in edges if e.dep.state not in cwr.WRITEOFF]
    print()
    print(f"NOT COUNTED ABOVE, and it is a floor rather than a total: {len(invisible)} "
          f"of the {len(edges)} pointer rows are not write-offs, so the classifier "
          f"publishes no verdict for them and this diff cannot see them move.")
    by_state = collections.Counter(r.state for r in invisible)
    for st, n in by_state.most_common():
        print(f"  {st:24s} {n:3d}")
    print("  " + ", ".join(sorted(r.key for r in invisible)))
    # A CLAIM ABOUT ROWS THAT SURVIVED EVERY PLANT MAY ONLY BE MADE BY A RUN THAT
    # PLANTED AT EVERY SLOT. On a single plant this list would silently include 43 rows
    # nothing was planted near -- an artifact claiming more than it ran, which is the
    # exact half-truth this wave is auditing the census for.
    if sweep:
        robust = [e.dep.key for e in edges
                  if e.dep.state in cwr.WRITEOFF and e.dep.key not in silent_rows]
        print()
        print(f"WRITE-OFF pointer rows that survived EVERY slot unchanged: {len(robust)}"
              + (f" -- {', '.join(sorted(robust))}" if robust else ""))
        print("  A pointer whose own cell already carries the argument is not fragile. "
              "That is the shape\n  the fix gives the other rows, and it is worth "
              "seeing it already working.")
    else:
        print()
        print("ROWS THAT SURVIVE: not reported. One plant cannot support a claim about "
              "rows nothing\n  was planted near. Run --plant-sweep for that number.")

    # AN EMPTY RESULT IS A LOUD EVENT HERE, NEVER A SILENT PASS. A sweep that plants
    # rows and finds nothing has either fixed the census or broken the harness, and
    # those must not look alike.
    if totals["slots"] and not totals["row_kind_changes"]:
        print()
        print(f"REFUSED after planting {reason!r} at every slot: every planted row "
              f"left every verdict identical. Either the "
              "positional dialect is gone from this census -- in which case this "
              "instrument is obsolete and should be deleted -- or this harness is not "
              "planting what it thinks it is. It is NOT reported as a pass.")
        return 1
    return 0


# --------------------------------------------------------------------------------------
# THE GUARD: pin the graph, then fail when it moves under a row nobody edited
# --------------------------------------------------------------------------------------
PIN = ROOT / "_audit" / "_census" / "pointer-graph.tsv"

#: WHY THE PIN CARRIES THE DONOR'S *KIND* AND NOT ITS TEXT. There are two ways a
#: positional pointer's argument changes with no edit to the pointer: the donor is
#: RE-POINTED (a row was inserted between them) or the donor's own reason is REWRITTEN.
#: Pinning the donor's prose would catch the second -- and would also go red every time
#: a wave appends a correction to a cell, which happens here several times a day. A
#: guard that cries wolf gets switched off, and a switched-off guard is worse than none.
#: So the pin carries the CONSEQUENCE rather than the evidence: the donor's classified
#: kind. A cosmetic append is silent; a rewrite that changes what the dependent inherits
#: is loud. The cost is stated rather than hidden -- a donor rewrite that changes the
#: ARGUMENT without changing its KIND passes this guard, and nothing here would see it.
PIN_HEADER = ("dependent\tdonor\tread_distance\tdonor_kind\tdependent_state\t"
              "slice\tdependent_reason_head\n")


def pin_rows(ref: str | None = None) -> list[tuple[str, ...]]:
    rows, edges, orphans, by_table, _d, _s = build_graph(ref)
    kinds = {}
    try:
        all_rows, wo, _dia, _st, _rul, _pr, _adj = cwr.build(ref)
        kinds = {r.key: (r.kind or "|".join(sorted(r.kinds)) or "-") for r in all_rows}
    except Exception as exc:                      # pragma: no cover - reported, not hidden
        print(f"WARNING: the classifier would not run ({exc.__class__.__name__}: "
              f"{exc}); donor kinds are pinned as UNKNOWN and this guard is running "
              f"on half its evidence.")
    out = []
    for e in sorted(edges, key=lambda e: (e.dep.letter, e.dep.lineno)):
        out.append((
            e.dep.key, e.donor.key, str(e.read_distance),
            kinds.get(e.donor.key, "UNKNOWN"), e.dep.state,
            ccs.SLICES[e.dep.letter],
            e.dep.reason[:48].replace("\t", " ").replace("|", "/"),
        ))
    return out


def write_pin(ref: str | None = None) -> int:
    rows = pin_rows(ref)
    PIN.parent.mkdir(parents=True, exist_ok=True)
    with PIN.open("w", encoding="ascii", errors="replace", newline="\n") as fh:
        fh.write(PIN_HEADER)
        for r in rows:
            fh.write("\t".join(r) + "\n")
    per = collections.Counter(r[5] for r in rows)
    print(f"pinned {len(rows)} positional pointers to {PIN}")
    for name in ccs.SLICES.values():
        print(f"  {name:30s} {per.get(name, 0):3d}")
    return 0


def check_pin(ref: str | None = None) -> int:
    """Fail when a pointer's argument moved without that pointer being edited.

    THE ASSERTION IS PER SLICE, NEVER OVER THE UNION. If `network.md` lost every
    pointer it has, a union count of 69 would still be within a few of 65 and nothing
    would say a source had gone dark. A union assertion over a redundant corpus cannot
    detect a lost source, so each slice is checked against its own pinned count.
    """
    if not PIN.exists():
        print(f"REFUSED: no pin at {PIN}. Run --pin first. A guard with no baseline "
              f"is not a guard that passes, it is a guard that never ran.")
        return 1
    lines = PIN.read_text(encoding="ascii", errors="replace").splitlines()
    if len(lines) < 2:
        print(f"REFUSED: the pin at {PIN} holds a header and no rows. AN ASSERTION "
              f"SATISFIED BY AN EMPTY RESULT CANNOT FAIL, so this is reported as a "
              f"defect in the pin rather than as a clean census.")
        return 1
    # EVERY FIELD IS STRIPPED. The pin is written with LF and `core.autocrlf` turns it
    # into CRLF on checkout, which leaves a trailing `\r` on the LAST column. Today that
    # column is only printed, so the guard would not have broken -- it would have started
    # quoting a stray control character, and the next person to add a column after it
    # would have found the comparison silently failing on a byte nobody typed.
    want = {}
    for line in lines[1:]:
        c = [f.strip() for f in line.split("\t")]
        if len(c) < 7 or not c[0]:
            print(f"REFUSED: the pin holds a row with {len(c)} field(s) where 7 are "
                  f"expected: {line[:80]!r}")
            return 1
        want[c[0]] = c
    have = {r[0]: list(r) for r in pin_rows(ref)}

    print("THE POINTER-GRAPH GUARD")
    print("=" * 92)
    print(f"pinned pointers : {len(want)}      measured now : {len(have)}")

    problems: list[str] = []
    dark: list[str] = []
    for name in ccs.SLICES.values():
        w = sum(1 for c in want.values() if c[5] == name)
        h = sum(1 for c in have.values() if c[5] == name)
        verdict = "ok" if w == h else "MOVED"
        print(f"  {name:30s} pinned {w:3d}   now {h:3d}   {verdict}")
        if w and not h:
            dark.append(
                f"{name} contributed ZERO positional pointers, against {w} pinned. "
                f"Either every one was rewritten -- in which case re-pin and say so "
                f"in the commit -- or this slice stopped parsing.")
    # PRINTED, not merely counted. The first version of this built the sentence and
    # dropped it into the failure tally without ever putting it on the terminal, so a
    # reader saw a count and no cause -- a refusal that names only what it did not
    # match is half a measurement, and this was less than half.
    print()
    print(f"SOURCE WENT DARK -- a slice lost every pointer it had: {len(dark)}")
    for d in dark:
        print(f"  {d}")
    problems.extend(dark)

    repointed, kindmoved, gone, new, moved_dist = [], [], [], [], []
    for key, w in want.items():
        h = have.get(key)
        if h is None:
            gone.append(key)
            continue
        if w[1] != h[1]:
            repointed.append(f"{key} was reading its argument off {w[1]} and now "
                             f"reads it off {h[1]}. NOTHING IN {key}'s OWN LINE HAD "
                             f"TO CHANGE FOR THAT TO HAPPEN.")
        elif w[3] != h[3]:
            kindmoved.append(f"{key} still points at {w[1]}, but {w[1]}'s verdict "
                             f"moved {w[3]} -> {h[3]}, so {key} now rests on a "
                             f"different argument than when it was pinned.")
        elif w[2] != h[2]:
            moved_dist.append(f"{key} still reaches {w[1]}, but the walk is now "
                              f"{h[2]} rows instead of {w[2]} -- rows moved between "
                              f"them without breaking the link.")
    for key in have:
        if key not in want:
            new.append(f"{key} is a NEW positional pointer ({have[key][6]!r} -> "
                       f"{have[key][1]}). It is not an error, and it is not silent: "
                       f"re-pin to accept it.")

    # A ROW THAT IS BOTH RE-POINTED AND KIND-MOVED IS REPORTED ONCE, AS RE-POINTED.
    # That is the stronger finding and the one that names the cause; saying it twice
    # would inflate the count this guard is read by.
    for label, items, fatal in (
            ("RE-POINTED -- an argument changed under a row nobody edited",
             repointed, True),
            ("DONOR VERDICT MOVED -- the inherited argument is not the pinned one",
             kindmoved, True),
            ("POINTER GONE -- a pinned pointer is no longer in the census",
             gone, True),
            ("READ DISTANCE MOVED -- same donor, longer walk", moved_dist, False),
            ("NEW POINTER", new, False)):
        print()
        print(f"{label}: {len(items)}")
        for it in items:
            print(f"  {it}")
        if fatal:
            problems.extend(items)

    if problems:
        print()
        print(f"FAILED -- {len(problems)} pinned pointer(s) moved. Every one of them is "
              f"a row whose write-off argument changed\nwithout that row being edited. "
              f"If the change was intended, re-pin with --pin and say so in the commit "
              f"message;\nif it was not, the insertion that caused it is the bug.")
        return 1
    print()
    print(f"PASS -- all {len(want)} pinned pointers still read the argument they were "
          f"pinned against.\nWHAT THIS DID NOT CHECK, stated so the pass is not read "
          f"as wider than it is: a donor rewrite that\nchanges the ARGUMENT without "
          f"changing its KIND, and the {len(new)} pointer(s) added since the pin.")
    return 0


# --------------------------------------------------------------------------------------
# THE RED PROOFS. A guard that has not been shown failing certifies nothing.
# --------------------------------------------------------------------------------------
def _sandbox_with_pin(box: pathlib.Path) -> pathlib.Path:
    """A sandbox that carries the WORKING TREE's scripts and census, not HEAD's.

    `make_sandbox` deliberately uses `git archive HEAD` so an uncommitted edit cannot
    leak into a MEASUREMENT. The selftest is the opposite case: the thing on trial is
    this file, which is uncommitted, and the baseline is the pin, which is uncommitted
    too. A sandbox at HEAD would not contain either, and every control would go red for
    a reason that has nothing to do with the census -- which is exactly what the first
    run of this selftest did, calibration included. Overlaying is stated here rather
    than done quietly, because it is a real weakening: this control runs against my
    working copy, so it proves the guard convicts, not that HEAD does.
    """
    tree = make_sandbox(box)
    for src in (ROOT / "scripts").glob("*.py"):
        shutil.copy2(src, tree / "scripts" / src.name)
    for src in (ROOT / "_audit" / "_census").iterdir():
        if src.is_file():
            shutil.copy2(src, tree / "_audit" / "_census" / src.name)
    assert (tree / "scripts" / "measure_pointer_graph.py").exists()
    assert (tree / "_audit" / "_census" / "pointer-graph.tsv").exists(), \
        "the pin must be in the sandbox or every control is meaningless"
    return tree


def _check_in(tree: pathlib.Path) -> tuple[str, int]:
    env = dict(os.environ)
    env["GIT_DIR"] = str(gitdir())
    p = subprocess.run([sys.executable,
                        str(tree / "scripts" / "measure_pointer_graph.py"), "--check"],
                       capture_output=True, env=env)
    return (p.stdout + p.stderr).decode("utf-8", errors="replace"), p.returncode


def _slice_path(tree: pathlib.Path, letter: str) -> pathlib.Path:
    return tree / "_audit" / "_census" / ccs.SLICES[letter]


def _rewrite_cell(path: pathlib.Path, lineno: int, new_reason: str) -> None:
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    cells = ccs.cells(lines[lineno - 1])
    for j in range(len(cells) - 1, -1, -1):
        if cells[j].strip():
            break
    cells[j] = new_reason
    lines[lineno - 1] = "| " + " | ".join(cells) + " |"
    path.write_bytes(nl.join(lines).encode("utf-8"))


def selftest(box: pathlib.Path) -> int:
    """Plant each failure class and assert the guard convicts it -- or clears it.

    THE CALIBRATION IS NOT DECORATIVE. A harness where every mutation goes red is not
    discriminating, it is broken, so G5 changes something real and the guard MUST stay
    green. And every mutation asserts its POSTCONDITION before its verdict is believed:
    asserting that a mutation changed bytes is not asserting that it achieved its
    intent, which is a defect a sibling wave paid for in this same corpus today.
    """
    if not PIN.exists():
        print("REFUSED: --selftest needs a pin to mutate against. Run --pin first.")
        return 1
    rows, edges, orphans, by_table, _d, _s = build_graph(None)
    by_dep = {e.dep.key: e for e in edges}
    results: list[tuple[str, str, bool, str]] = []

    def record(name, want_red, out, rc, needle):
        red = rc != 0
        hit = needle in out
        ok = (red == want_red) and hit
        results.append((name, "RED" if red else "GREEN", ok,
                        f"expected {'RED' if want_red else 'GREEN'} carrying "
                        f"{needle!r}; {'found' if hit else 'DID NOT FIND'} it"))

    # -- G1 RE-POINT: plant one substantive row above a dependent ---------------------
    tree = _sandbox_with_pin(box)
    e = by_dep["P D15"]
    p = _slice_path(tree, "P")
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    tmpl = ccs.cells(lines[e.dep.lineno - 1])
    planted = plant_line(e.dep, tmpl)
    assert planted, "G1 postcondition: the anchor must be able to host a planted row"
    lines.insert(e.dep.lineno - 1, planted)
    p.write_bytes(nl.join(lines).encode("utf-8"))
    assert "PLANT1" in p.read_text(encoding="utf-8"), "G1 postcondition: plant landed"
    out, rc = _check_in(tree)
    record("G1 re-point (plant a row above P D15)", True, out, rc,
           "P D15 was reading its argument off P D14 and now reads it off P PLANT1")

    # -- G2 DONOR REWRITE: same donor, different argument ----------------------------
    tree = _sandbox_with_pin(box)
    donor = by_dep["P D15"].donor
    p = _slice_path(tree, donor.letter)
    _rewrite_cell(p, donor.lineno, PLANT_REASON)
    assert PLANT_REASON in p.read_text(encoding="utf-8"), \
        "G2 postcondition: the donor's reason really was rewritten"
    out, rc = _check_in(tree)
    record("G2 donor rewrite (P D14's own reason replaced)", True, out, rc,
           "P D14's verdict moved")

    # -- G3 A SLICE GOES DARK: assert PER SLICE, never over the union -----------------
    tree = _sandbox_with_pin(box)
    p = _slice_path(tree, "J")
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    for ed in [x for x in edges if x.dep.letter == "J"]:
        cells = ccs.cells(lines[ed.dep.lineno - 1])
        for j in range(len(cells) - 1, -1, -1):
            if cells[j].strip():
                break
        cells[j] = PLANT_REASON
        lines[ed.dep.lineno - 1] = "| " + " | ".join(cells) + " |"
    p.write_bytes(nl.join(lines).encode("utf-8"))
    out, rc = _check_in(tree)
    record("G3 jobs.md loses every pointer (56 remain elsewhere -- a union "
           "assertion would pass)", True, out, rc,
           "jobs.md contributed ZERO positional pointers")

    # -- G4 EMPTY PIN -----------------------------------------------------------------
    tree = _sandbox_with_pin(box)
    (tree / "_audit" / "_census" / "pointer-graph.tsv").write_text(
        PIN_HEADER, encoding="ascii", newline="\n")
    out, rc = _check_in(tree)
    record("G4 pin holds a header and no rows", True, out, rc,
           "AN ASSERTION SATISFIED BY AN EMPTY RESULT CANNOT FAIL")

    # -- G5 CALIBRATION: a real edit that must NOT fire -------------------------------
    tree = _sandbox_with_pin(box)
    p = _slice_path(tree, "P")
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    i = by_dep["P D15"].dep.lineno - 1
    cells = ccs.cells(lines[i])
    before_cap = cells[1]
    cells[1] = cells[1] + "  "
    lines[i] = "| " + " | ".join(cells) + " |"
    p.write_bytes(nl.join(lines).encode("utf-8"))
    assert p.read_bytes().decode("utf-8") != raw, \
        "G5 postcondition: the calibration must really change the file"
    out, rc = _check_in(tree)
    # 67 since the live lane's merge, 2026-09-24 (69 before): `N 134` gained
    # evidence of its own and `N 135`'s vestigial "Same" was written out, so
    # the pin lost both pointers in the same commit as this literal.
    # 66 since lane L7's merge, 2026-09-24: `P G3` names its ruling in
    # place of its positional 'same ruling', so it is no longer a pointer.
    record("G5 CALIBRATION -- whitespace in P D15's capability cell", False, out, rc,
           "PASS -- all 66 pinned pointers")

    print("THE POINTER-GRAPH GUARD, SHOWN FAILING")
    print("=" * 92)
    print(f"{'mutation':70s} {'verdict':8s} ok")
    bad = 0
    for name, verdict, ok, note in results:
        print(f"{name:70s} {verdict:8s} {'yes' if ok else 'NO'}")
        if not ok:
            bad += 1
            print(f"    {note}")
    print()
    if bad:
        print(f"REFUSED: {bad} of {len(results)} controls did not behave as specified. "
              f"A guard whose own\nred-proof does not reproduce is not admitted to the "
              f"register.")
        return 1
    print(f"all {len(results)} controls behaved as specified, including the calibration "
          f"-- a harness where\nevery mutation goes red is not discriminating, it is "
          f"broken.")
    print(f"CALIBRATION CELL (unchanged capability text): {before_cap[:60]!r}")
    return 0


def _in_own_sandbox(given: str, prefix: str, run) -> int:
    """`run(sandbox)`, in the caller's `--sandbox` or in a directory no other run uses.

    With `--sandbox`, exactly as before: that path, owned by the caller, left in place.
    Without it, a FRESH directory from `mkdtemp`, removed when the run ends, passed or
    failed -- the default used to be one fixed path, and because `make_sandbox` starts
    with an `rmtree`, two concurrent runs deleted each other's sandbox mid-check. The
    tree sits one level inside, so `sandbox.parent`, where `plant` writes its two TSVs,
    is this run's directory and not the shared temp root.
    """
    if given:
        return run(pathlib.Path(given))
    import tempfile
    run_dir = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
    try:
        return run(run_dir / "tree")
    finally:
        # A failed removal must not turn the verdict above into a crash, and must not
        # pass in silence either: nothing else will ever delete this directory.
        shutil.rmtree(run_dir, ignore_errors=True)
        if run_dir.exists():
            print(f"WARNING: could not remove this run's sandbox {run_dir}; it is "
                  f"left behind and nothing else will delete it.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Measure the positional pointer graph")
    ap.add_argument("--selftest", action="store_true",
                    help="plant every failure class and assert the guard convicts it")
    ap.add_argument("--pin", action="store_true",
                    help="write the pointer graph to _audit/_census/pointer-graph.tsv")
    ap.add_argument("--check", action="store_true",
                    help="fail if any pinned pointer's argument moved")
    ap.add_argument("--ref", default=None)
    ap.add_argument("--edges", action="store_true", help="print every pointer edge")
    ap.add_argument("--plant", default="", metavar="ROW",
                    help="plant one row directly above ROW and diff the verdicts")
    ap.add_argument("--plant-sweep", action="store_true",
                    help="plant a row at EVERY exposed slot")
    ap.add_argument("--plant-reason", default=PLANT_REASON,
                    help="the reason cell the planted row carries. THE RED-PROOF "
                         "HANDLE: plant a non-substantive cell (--plant-reason same) "
                         "and the sweep must REFUSE, because a row that cannot become "
                         "a donor must not be reported as evidence of safety")
    ap.add_argument("--sandbox", default="",
                    help="where to build the throwaway tree. Default: a fresh directory "
                         "per run under the system temp directory, removed when the run "
                         "ends (one fixed path let two concurrent runs delete each "
                         "other's sandbox). A path given here is kept afterwards")
    args = ap.parse_args(argv)

    if args.selftest:
        return _in_own_sandbox(args.sandbox, "pointer-graph-selftest-", selftest)
    if args.pin:
        return write_pin(args.ref)
    if args.check:
        return check_pin(args.ref)
    if args.plant or args.plant_sweep:
        return _in_own_sandbox(
            args.sandbox, "pointer-graph-sandbox-",
            lambda box: plant(args.plant or None, args.plant_sweep, box,
                              args.plant_reason))
    return report(args.ref, args.edges)


if __name__ == "__main__":
    sys.exit(main())
