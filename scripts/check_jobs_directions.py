"""The jobs slice's direction column, kept TRUE: one line per still-GAP row.

THE QUESTION. ``scripts/census_completion.py`` cannot place a single
``_audit/_census/jobs.md`` row in bucket 2 (writes) or bucket 3 (reads),
because that census's per-row tables carry no R/W column -- 56 rows print as
``direction unknown``. ``_audit/2026-09-21-the-jobs-direction.md`` section 8
argues the census should NOT grow the column: section 2 already carries
direction per ROW-RANGE, and a per-row copy inside the census would drift
from it. So the per-row reading lives OUTSIDE the census, in
``_audit/_census/jobs-directions.tsv``, and this file keeps it true.

It exits 1 when:

  * a still-GAP jobs row has no line (a row entered GAP and nobody classified
    it), or a line names a row that is no longer GAP (it was built or ruled and
    its line was left pointing at nothing);
  * a line's ``dir_phrase`` -- the words that decide its direction -- is no
    longer written in the row's own capability cell;
  * a line's ``dir_basis`` is no longer borne out by section 2 of ``jobs.md``:
    a ``VERB`` row whose single-direction range now disagrees, or a
    ``VERB-OVER-RANGE`` row whose recorded disagreement has gone;
  * a recorded ``is_read_url``, refusal kind or ``also_driven`` verdict
    disagrees with the LIVE boundary;
  * a source no longer resolves (the file, a ``::token`` in it, or a census
    row it cites);
  * any break in the vocabulary.

THE BOUNDARY IS IMPORTED, NEVER RE-IMPLEMENTED -- and neither is the bucket-3
instrument. Every function that drives an address, and the whole vocabulary
of the read-address columns, is ``scripts/check_read_addresses.py``'s: its
``shape_problems``, ``boundary_problems``, ``control_problems`` and
``refusal_of`` are called on this table's read rows unchanged. The two tables
therefore cannot come to mean different things by the same column name.

AND THE IMPORT OF THE BOUNDARY STAYS LAZY, for the reason that file gives:
``census_completion.py`` is meant to count this table, and
``scripts/_check_census_completion_can_fail.py`` runs it inside a copy of the
tree with no ``linkedin_server`` package. ``load``, ``coverage_problems``,
``shape_problems``, ``split``, ``census_figures`` and ``report_lines`` touch
no boundary and read no file but the table.

SHOWN FAILING: ``tests/test_jobs_directions.py`` plants each defect above
into a COPY of the real table and asserts red AND the planted row named,
including the two CONSISTENT lies only the live boundary can convict.

WHAT IT DOES NOT CHECK. The judgement columns -- which page is a row's
address, the gate past an admitted boundary, and above all whether a row
READS or WRITES -- are checked for vocabulary, for consistency and for being
anchored in text that still exists. Nothing offline can check that LinkedIn
serves an address (ALLOWED IS NOT SERVED), and no instrument can check that a
direction is RIGHT: ``dir_phrase`` proves the deciding words are still there,
not that they were read correctly.

    python scripts/check_jobs_directions.py
    python scripts/check_jobs_directions.py --table <a copy>   # for controls
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import check_read_addresses as cra  # noqa: E402  (the bucket-3 instrument)
import count_census_states as ccs  # noqa: E402  (the shipped census parser)

ROOT = _HERE.parent
TABLE = ROOT / "_audit" / "_census" / "jobs-directions.tsv"
JOBS = ccs.CENSUS / ccs.SLICES["J"]

COLUMNS = ("slice", "row", "dir", "dir_phrase", "dir_basis", "class",
           "address", "basis", "source_kind", "source", "is_read_url",
           "refusal", "gate", "also_driven", "note")

#: Every still-GAP row reads, writes, or names both. There is no fourth word:
#: the one row the 2026-09-21 wave held as AMBIGUOUS is RESOLVED in its note.
DIRECTIONS = ("R", "W", "R+W")

#: How a row's direction was decided. See the table's own header.
DIR_BASES = ("VERB", "VERB-OVER-RANGE", "COMPOUND", "RESOLVED")

#: The read-address classes are the bucket-3 table's, plus one for a row that
#: has no read half at all -- it is the write lane's, and carries no address.
WRITE_CLASS = "WRITE"
CLASSES = cra.CLASSES + (WRITE_CLASS,)
GATES = cra.GATES

SLICE = "J"


def load(path: pathlib.Path = TABLE) -> tuple[list[dict[str, str]], list[str]]:
    """(rows, problems). Parses the table and does nothing else.

    ``#`` lines are commentary. The first other line must be the column
    header, spelled exactly. A missing or non-ASCII table is a PROBLEM, never
    an empty table: zero rows would read as zero coverage for a reason nobody
    could see.
    """
    rows: list[dict[str, str]] = []
    problems: list[str] = []
    try:
        text = path.read_text(encoding="ascii")
    except FileNotFoundError:
        return rows, [f"{path.name}: the jobs direction table does not exist "
                      f"at {path.parent.name}/{path.name}"]
    except UnicodeDecodeError as exc:
        return rows, [f"{path.name}: not ASCII ({exc.reason} at byte "
                      f"{exc.start})"]
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    if not lines or tuple(lines[0].split("\t")) != COLUMNS:
        return rows, [f"{path.name}: the header is not exactly "
                      f"{'<TAB>'.join(COLUMNS)}"]
    for number, line in enumerate(lines[1:], start=2):
        cells = line.split("\t")
        if len(cells) != len(COLUMNS):
            problems.append(f"data line {number}: {len(cells)} cells, want "
                            f"{len(COLUMNS)}")
            continue
        rows.append(dict(zip(COLUMNS, cells)))
    return rows, problems


def key(row: dict[str, str]) -> tuple[str, str]:
    return row["slice"], row["row"]


def _tag(row: dict[str, str]) -> str:
    return f"{row['slice']} {row['row']}"


def population() -> dict[tuple[str, str], str]:
    """(slice, row id) -> census direction for every still-GAP jobs row, today.

    TAKEN FROM ``census_completion.walk()``, the walk that prints the 56, so
    this table is checked against exactly the population the completion
    figure is computed over. Imported inside the function because
    ``census_completion`` is meant to import THIS module.
    """
    import census_completion as cc

    return {(letter, rid): direction
            for letter, rid, state, direction in cc.walk()
            if letter == SLICE and state == "GAP"}


def coverage_problems(rows: list[dict[str, str]],
                      pop: dict[tuple[str, str], str]) -> list[str]:
    """Every still-GAP jobs row exactly once, and nothing else.

    BOTH DIRECTIONS OF DRIFT, for the reason ``check_read_addresses`` gives:
    a MISSING line is a row nobody classified, and an EXTRA line is a row that
    was built or ruled and whose direction now describes nothing.

    AND ONE CHECK THAT WAITS FOR A DAY THAT MAY NEVER COME: if ``jobs.md``
    ever does grow a direction cell, ``census_completion.walk()`` will start
    returning it, and it must then agree with this table rather than quietly
    becoming a second opinion.
    """
    problems: list[str] = []
    counted = collections.Counter(key(r) for r in rows)
    for k, n in sorted(counted.items()):
        if n > 1:
            problems.append(f"{k[0]} {k[1]}: {n} lines, want exactly one")
    for k in sorted(set(pop) - set(counted)):
        problems.append(f"{k[0]} {k[1]}: a still-GAP jobs row today with NO "
                        f"line in the table -- nobody has classified it")
    for k in sorted(set(counted) - set(pop)):
        problems.append(f"{k[0]} {k[1]}: has a line but is NOT a still-GAP "
                        f"jobs row today -- it left GAP and its line points "
                        f"at nothing")
    for r in rows:
        census_dir = pop.get(key(r))
        if census_dir in DIRECTIONS and census_dir != r["dir"]:
            problems.append(f"{_tag(r)}: dir {r['dir']!r} but the census now "
                            f"carries a direction cell reading {census_dir!r}")
    return problems


def _reads(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [r for r in rows if r["dir"] in cra.DIRECTIONS]


def shape_problems(rows: list[dict[str, str]]) -> list[str]:
    """The vocabulary, and the consistency a reader of each column relies on.

    THE READ ROWS ARE HANDED TO ``check_read_addresses.shape_problems``
    UNCHANGED, so a read row here obeys exactly the rules a bucket-3 row does.
    What is checked here is only what that table does not have: the direction
    columns, and the WRITE class.
    """
    problems: list[str] = []
    for r in rows:
        tag = _tag(r)
        if r["slice"] != SLICE:
            problems.append(f"{tag}: slice {r['slice']!r} is not {SLICE!r}")
        if not re.fullmatch(r"[0-9]{1,3}", r["row"]):
            problems.append(f"{tag}: row id {r['row']!r} is not a jobs row "
                            f"number")
        d = r["dir"]
        if d not in DIRECTIONS:
            problems.append(f"{tag}: dir {d!r} is off {DIRECTIONS}")
            continue
        basis = r["dir_basis"]
        if basis not in DIR_BASES:
            problems.append(f"{tag}: dir_basis {basis!r} is off {DIR_BASES}")
        parts = [p.strip() for p in r["dir_phrase"].split(" + ")]
        if any(not p for p in parts) or not r["dir_phrase"].strip():
            problems.append(f"{tag}: dir_phrase is empty or has an empty part")
        if d == "R+W" and len(parts) != 2:
            problems.append(f"{tag}: an R+W row names its read word AND its "
                            f"write word, '<read> + <write>'")
        if d != "R+W" and len(parts) != 1:
            problems.append(f"{tag}: only an R+W row carries two deciding "
                            f"phrases")
        if basis in ("COMPOUND", "RESOLVED") and d != "R+W":
            problems.append(f"{tag}: dir_basis {basis} is for an R+W row, "
                            f"and this row is {d}")
        if basis == "RESOLVED" and len(r["note"].strip()) < 80:
            problems.append(f"{tag}: a RESOLVED direction must argue the call "
                            f"in its note")
        if (d == "W") != (r["class"] == WRITE_CLASS):
            problems.append(f"{tag}: class {r['class']!r} with dir {d}: a "
                            f"row is WRITE exactly when it has no read half")
        if r["class"] == WRITE_CLASS:
            for column in ("address", "basis", "is_read_url", "refusal",
                           "also_driven"):
                if r[column] != "-":
                    problems.append(f"{tag}: a WRITE row carries no address, "
                                    f"so {column} must be '-'")
            if r["gate"] != "n/a":
                problems.append(f"{tag}: a WRITE row's gate must be 'n/a'")
            if r["source_kind"] not in cra.SOURCE_KINDS:
                problems.append(f"{tag}: source_kind {r['source_kind']!r} is "
                                f"off {cra.SOURCE_KINDS}")
            if not r["source"].strip() or r["source"] == "-":
                problems.append(f"{tag}: no source named")
            if len(r["note"].strip()) < 20:
                problems.append(f"{tag}: a WRITE row still says in its note "
                                f"what it writes")
    problems += cra.shape_problems(_reads(rows))
    return problems


def _capabilities(path: pathlib.Path = JOBS) -> dict[str, str]:
    """Row id -> capability cell, off the SHIPPED census parser.

    ``ccs.cells`` honours the markdown escape for a literal pipe; a hand-rolled
    split reads the tail of such a cell and looks like it worked.
    """
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|") or not ccs.ROW.match(line):
            continue
        c = ccs.cells(line)
        if len(c) < 3 or c[0].lower() in ccs.HEADERS:
            continue
        if c[0] and set(c[0]) <= set("-: "):
            continue
        out.setdefault(c[0], c[1])
    return out


def phrase_problems(rows: list[dict[str, str]],
                    path: pathlib.Path = JOBS) -> list[str]:
    """Every deciding phrase is still written in the row's own capability cell.

    A DIRECTION IS A READING OF WORDS, SO THE WORDS ARE CITED. If a later
    wave rewrites a capability -- ``Filter`` becomes ``Save a filter`` -- the
    direction recorded here may no longer follow, and this is how that is
    found rather than inherited. Word-bounded and case-blind.
    """
    problems: list[str] = []
    caps = _capabilities(path)
    for r in rows:
        cap = caps.get(r["row"])
        if cap is None:
            problems.append(f"{_tag(r)}: no capability cell for this row in "
                            f"{path.name}")
            continue
        for part in (p.strip() for p in r["dir_phrase"].split(" + ")):
            if part and not re.search(
                    rf"(?<![A-Za-z0-9]){re.escape(part)}(?![A-Za-z0-9])",
                    cap, re.I):
                problems.append(f"{_tag(r)}: dir_phrase {part!r} is no longer "
                                f"written in the row's capability cell")
    return problems


def range_problems(rows: list[dict[str, str]]) -> list[str]:
    """``dir_basis`` against section 2 of ``jobs.md``, re-read on every run.

    Section 2 files direction by ROW-RANGE, and a range cell is a claim about
    a BLOCK. ``VERB`` says the row's own words agree with it (or that it names
    no single direction); ``VERB-OVER-RANGE`` says they DISAGREE, and records
    it. Either claim goes stale the moment somebody edits section 2, so both
    are re-checked against the shipped range reader, imported rather than
    copied.
    """
    import _check_jobs_range_directions as jrd

    resolved, _unresolved = jrd.jobs_directions()
    problems: list[str] = []
    for r in rows:
        ranged = resolved.get(f"{SLICE} {r['row']}")
        basis, d = r["dir_basis"], r["dir"]
        if basis == "VERB" and ranged is not None and ranged != d:
            problems.append(f"{_tag(r)}: dir_basis VERB, but section 2's range "
                            f"now files it {ranged} against dir {d} -- either "
                            f"the row or the range moved")
        if basis == "VERB-OVER-RANGE":
            if ranged is None:
                problems.append(f"{_tag(r)}: dir_basis VERB-OVER-RANGE, but no "
                                f"single-direction range covers the row any "
                                f"more")
            elif ranged == d:
                problems.append(f"{_tag(r)}: dir_basis VERB-OVER-RANGE, but "
                                f"section 2 now AGREES ({ranged}) -- the "
                                f"recorded disagreement is stale")
    return problems


_SOURCE = re.compile(
    r"^([A-Za-z0-9_.\-/]+\.(?:py|md|tsv|json|html))"
    r"(?:::([A-Za-z_][A-Za-z0-9_\-]*))?(?: row ([A-Za-z]*\d+[a-z]?))?$")


def source_problems(rows: list[dict[str, str]],
                    root: pathlib.Path = ROOT) -> list[str]:
    """Every source still RESOLVES: the file, the ``::token``, the census row.

    The shape is ``check_read_addresses``' with two widenings, both needed by
    real rows: a committed FIXTURE may be the source (``.html``), because an
    address drawn on a capture is recorded nowhere else; and a token may
    carry a hyphen, because the route a fixture draws is spelled with one.
    The whole cell must match -- trailing prose is not a citation.
    """
    problems: list[str] = []
    for r in rows:
        found = _SOURCE.match(r["source"])
        if not found:
            problems.append(f"{_tag(r)}: source {r['source']!r} is not "
                            f"'<path>[::token][ row <id>]'")
            continue
        path = root / found.group(1)
        if not path.is_file():
            problems.append(f"{_tag(r)}: source file {found.group(1)} does "
                            f"not exist")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        token = found.group(2)
        if token and not re.search(
                rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", text):
            problems.append(f"{_tag(r)}: source token {token} is no longer "
                            f"spelled in {found.group(1)}")
        cited = found.group(3)
        if cited:
            if not found.group(1).startswith("_audit/_census/"):
                problems.append(f"{_tag(r)}: a 'row' citation names a census "
                                f"row, and {found.group(1)} is not a census "
                                f"slice")
            elif not re.search(rf"(?m)^\|\s*{re.escape(cited)}\s*\|", text):
                problems.append(f"{_tag(r)}: source row {cited} is no longer "
                                f"a row of {found.group(1)}")
    return problems


def boundary_problems(rows: list[dict[str, str]]) -> list[str]:
    """Every recorded verdict against the LIVE boundary -- the bucket-3 code."""
    return cra.boundary_problems(_reads(rows))


def split(rows: list[dict[str, str]]) -> dict[str, int]:
    """The decomposition, counted off the dir, class and gate columns."""
    out = {f"dir:{d}": 0 for d in DIRECTIONS}
    out.update(collections.Counter(f"dir:{r['dir']}" for r in rows))
    reads = _reads(rows)
    classes = collections.Counter(r["class"] for r in reads)
    gates = collections.Counter(r["gate"] for r in reads
                                if r["class"] == "ADMITTED")
    forbidden = sum(1 for r in reads if r["class"] == "REFUSED"
                    and r["refusal"].startswith("FORBIDDEN["))
    out.update({f"class:{c}": classes[c] for c in cra.CLASSES})
    out.update({f"gate:{g}": gates[g] for g in GATES})
    out["refused:forbidden"] = forbidden
    out["refused:no_pattern"] = classes["REFUSED"] - forbidden
    out["blocked_on_nothing"] = sum(gates[g] for g in cra.BLOCKED_ON_NOTHING)
    out["reads"] = len(reads)
    out["rows"] = len(rows)
    return out


def census_figures(walk_rows, path: pathlib.Path = TABLE
                   ) -> tuple[dict[str, int] | None, list[str]]:
    """(figures, problems) for ``census_completion.report`` -- PURE.

    ``walk_rows`` is ``census_completion.walk()``'s output, passed in so this
    imports nothing from that module. The figures are WITHHELD (None) on any
    problem, never zeroed: a split over a table that has drifted from the
    census is a figure about a population nobody has.
    """
    pop = {(letter, rid): d for letter, rid, st, d in walk_rows
           if letter == SLICE and st == "GAP"}
    table, problems = load(path)
    problems += coverage_problems(table, pop)
    problems += shape_problems(table)
    if problems:
        return None, problems
    s = split(table)
    return {
        "jobs_gap": len(pop),
        "jobs_dir_r": s["dir:R"],
        "jobs_dir_w": s["dir:W"],
        "jobs_dir_rw": s["dir:R+W"],
        "jobs_admitted": s["class:ADMITTED"],
        "jobs_refused": s["class:REFUSED"],
        "jobs_no_address": s["class:NO-ADDRESS"],
        "jobs_needs_session": s["class:NEEDS-SESSION"],
        "jobs_undetermined": s["class:UNDETERMINED"],
        "jobs_blocked_on_nothing": s["blocked_on_nothing"],
    }, []


def report_lines(figures: dict[str, int] | None,
                 problems: list[str]) -> list[str]:
    """The lines ``census_completion.report`` prints for the jobs slice."""
    if figures is None:
        out = ["     JOBS SPLIT WITHHELD -- `_audit/_census/jobs-directions.tsv`",
               "     no longer covers today's still-GAP jobs rows, so any split",
               "     of it would describe a population the census does not have:"]
        out += [f"       !! {p}" for p in problems[:12]]
        if len(problems) > 12:
            out.append(f"       !! ... and {len(problems) - 12} more; run "
                       f"`scripts/check_jobs_directions.py`")
        return out
    reads = figures["jobs_dir_r"] + figures["jobs_dir_rw"]
    return [
        f"     jobs.md still-GAP rows, direction by side table   "
        f"{figures['jobs_gap']:4d}   `_audit/_census/jobs-directions.tsv`",
        f"       W    -> bucket 2                               "
        f"{figures['jobs_dir_w']:4d}   ENUMERATED, a phrase cited per row",
        f"       R    -> bucket 3                               "
        f"{figures['jobs_dir_r']:4d}",
        f"       R+W  -> bucket 3 (its read half)               "
        f"{figures['jobs_dir_rw']:4d}",
        f"     of the {reads} with a read half, the page each needs, MEASURED",
        f"     through the shipped boundary by `scripts/check_jobs_directions.py`:",
        f"       ADMITTED {figures['jobs_admitted']}, REFUSED "
        f"{figures['jobs_refused']}, NO-ADDRESS {figures['jobs_no_address']}, "
        f"NEEDS-SESSION {figures['jobs_needs_session']}, UNDETERMINED "
        f"{figures['jobs_undetermined']}",
        f"       BLOCKED ON NOTHING (a reader could be written today) "
        f"{figures['jobs_blocked_on_nothing']:4d}",
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Keep the jobs direction side "
                                 "table true against the census and the "
                                 "shipped read boundary.")
    ap.add_argument("--table", type=pathlib.Path, default=TABLE,
                    help="the table to check (default: the committed one)")
    args = ap.parse_args(argv)

    rows, problems = load(args.table)
    pop = population()
    problems += coverage_problems(rows, pop)
    problems += shape_problems(rows)
    problems += phrase_problems(rows)
    problems += range_problems(rows)
    problems += source_problems(rows)
    problems += cra.control_problems()
    problems += boundary_problems(rows)

    s = split(rows)
    driven = sum(1 for r in _reads(rows) if r["class"] in cra.WITH_ADDRESS)
    also = sum(len(cra._also(r)) for r in _reads(rows))
    print(f"still-GAP jobs rows today      {len(pop):4d}   census_completion.walk()")
    print(f"lines in the table             {len(rows):4d}   {args.table.name}")
    print(f"addresses re-driven            {driven:4d}   + {also} also_driven")
    print()
    print("    direction")
    for d in DIRECTIONS:
        print(f"      {d:14s} {s['dir:' + d]:4d}")
    print(f"    of the {s['reads']} with a read half, the page each needs:")
    for c in cra.CLASSES:
        print(f"      {c:14s} {s['class:' + c]:4d}")
    print(f"      REFUSED by a forbidden substring {s['refused:forbidden']}, "
          f"by allowlist silence {s['refused:no_pattern']}")
    print("    of the ADMITTED, the first thing past the boundary:")
    for g in GATES:
        print(f"      {g:16s} {s['gate:' + g]:4d}")
    print(f"    BLOCKED ON NOTHING           {s['blocked_on_nothing']:4d}   "
          f"ADMITTED and gate in {cra.BLOCKED_ON_NOTHING}")
    print()
    if problems:
        print(f"RED: {len(problems)} problem(s). The table no longer describes "
              f"the tree:")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"GREEN: {len(rows)} of {len(pop)} still-GAP jobs rows, every "
          f"deciding phrase still written, every recorded verdict agrees with "
          f"the live boundary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
