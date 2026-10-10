"""Check the next-step ledger and the capture queue against the census.

`_audit/_census/next-step.tsv` gives EVERY GAP row its next step, and
`_audit/_census/capture-queue.tsv` gives every live capture its surface, its
address, its presses and the rows it unblocks. Both are JUDGED tables
(`_audit/2026-09-28-lane-k-ledger.md`, sections 3 and 5). This file is what
keeps them honest as the census moves:

* EVERY GAP ROW EXACTLY ONCE. The population is the shipped walk,
  `census_completion.walk_cells()`, never a re-parse. A missing row is a row
  nobody has given a step; a doubled one is two answers; an extra one is a row
  that left GAP or never existed.
* THE COUNT RECONCILES with `census_completion`: the table's length equals the
  walk's still-GAP count and the counter's pinned `gap` figure.
* EVERY SOURCE RESOLVES: a census row id (`N 168`), a `path::phrase` whose
  phrase is in the file, or `RULING:<id>` registered and not superseded. All
  but the first form go through `check_write_classes.source_problems` -- the
  shipped resolver, imported, not rewritten.
* EVERY PAYLOAD RESOLVES: a CAPTURE id is a queue line that lists the row; a
  BUILD path is a tracked fixture or a PLANNED skeleton in the lane record; a
  RULING id is a question heading in the lane record; a SIBLING is a lane or a
  census row; an ADMIT address is one the read boundary refuses TODAY.
* THE QUEUE AGREES: every queue row is a census row; every capture-bound row
  sits on a queue line whose gate matches its step; every address verdict is
  re-driven through `readonly.is_read_url`.

Shown failing before it was trusted: `scripts/_check_next_step_can_fail.py`
plants a missing row, a duplicate, a dangling source, a CAPTURE id with no
queue line and a queue row that is no census row, and each is caught by name.

    python scripts/check_next_step.py
    python scripts/check_next_step.py --table COPY.tsv --queue COPY.tsv

Nothing here reaches LinkedIn, an account, or a browser.
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
_HERE = ROOT / "scripts"
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import census_completion as cc  # noqa: E402  (the shipped walk and pins)
import check_write_classes as cwc  # noqa: E402  (the shipped source resolver)

TABLE = ROOT / "_audit" / "_census" / "next-step.tsv"
QUEUE = ROOT / "_audit" / "_census" / "capture-queue.tsv"
RECORD = ROOT / "_audit" / "2026-09-28-lane-k-ledger.md"
JOBS_DIRECTIONS = ROOT / "_audit" / "_census" / "jobs-directions.tsv"

COLUMNS = ("row", "slice", "dir", "class", "next", "basis", "source")
QUEUE_COLUMNS = ("rank", "surface-id", "session", "needs", "address",
                 "address_verdict", "presses", "save", "loads", "searches",
                 "rows_unblocked", "rows_per_load", "rows", "captured_already",
                 "plan")
KINDS = ("CAPTURE", "ADMIT", "BUILD", "RULING", "PRECONDITION", "PURPOSE",
         "SIBLING", "TARGET")
BASES = ("MEASURED", "NAMED", "INFERRED")
#: The sibling lanes a row may be handed to. lane-NP since 2026-10-10: the
#: orchestrator's ruling 6 hands N 65 and N 178 to its details-page route.
LANES = ("lane-U", "lane-S", "lane-NP")
DIRECTIONS = ("R", "W", "R+W")

#: A census row id as this table cites one: the slice letter, a space, the id.
CENSUS_KEY = re.compile(r"^[JMNP] [A-Za-z0-9][A-Za-z0-9-]*$")
#: A tracked fixture cited bare, as the capture a step rests on.
FIXTURE = re.compile(r"^tests/fixtures/[A-Za-z0-9_./\-]+\.(?:html|txt)$")
#: The lane record's PLANNED block: a skeleton a builder will write.
PLANNED = re.compile(r"^\s+PLANNED (tests/fixtures/\S+) <- (.+)$", re.M)
#: The lane record's question headings.
QUESTION = re.compile(r"^### (Q-[A-Z0-9-]+)\b", re.M)


def _tsv(path: pathlib.Path, columns: tuple) -> tuple[list[dict], list[str]]:
    """(rows, problems): ASCII, the exact header, and the right cell count."""
    try:
        text = path.read_bytes().decode("ascii")
    except FileNotFoundError:
        return [], [f"{path.name}: does not exist"]
    except UnicodeDecodeError as exc:
        return [], [f"{path.name}: not ASCII ({exc.reason} at byte {exc.start})"]
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    if not lines or tuple(lines[0].split("\t")) != columns:
        return [], [f"{path.name}: the header is not exactly {'<TAB>'.join(columns)}"]
    rows, problems = [], []
    for number, line in enumerate(lines[1:], start=2):
        cells = line.split("\t")
        if len(cells) != len(columns):
            problems.append(f"{path.name} line {number}: {len(cells)} cells, want {len(columns)}")
            continue
        rows.append(dict(zip(columns, cells)))
    return rows, problems


def population() -> dict[str, tuple[str, str]]:
    """{"L id": (letter, direction)} for every GAP row, by the shipped walk."""
    return {f"{letter} {rid}": (letter, d)
            for letter, rid, st, d, _cells in cc.walk_cells() if st == "GAP"}


def _jobs_directions() -> dict[str, str]:
    rows, _ = _tsv_loose(JOBS_DIRECTIONS)
    return {f"J {r['row']}": r["dir"] for r in rows}


def _tsv_loose(path: pathlib.Path) -> tuple[list[dict], list[str]]:
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines()
             if ln and not ln.startswith("#")]
    head = lines[0].split("\t")
    return [dict(zip(head, ln.split("\t"))) for ln in lines[1:]], []


def _tracked(root: pathlib.Path) -> set[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "tests/fixtures"],
                         capture_output=True, text=True)
    return set(out.stdout.split())


def _boundary():
    """`readonly.is_read_url`, or None where the package is not importable."""
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from linkedin_server import readonly  # noqa: PLC0415
    except Exception:  # pragma: no cover - a tree copy with no package
        return None
    return readonly.is_read_url


def check(table: pathlib.Path = TABLE, queue: pathlib.Path = QUEUE,
          record: pathlib.Path = RECORD, root: pathlib.Path = ROOT):
    """(rows, queue_rows, problems, not_checked) -- every check, one run."""
    rows, problems = _tsv(table, COLUMNS)
    qrows, qproblems = _tsv(queue, QUEUE_COLUMNS)
    problems += qproblems
    not_checked: list[str] = []
    pop = population()
    index = cwc.census_index(root)
    jd = _jobs_directions()
    wclass = {r["key"]: r["class"] for r in cwc.load()[0]}
    record_text = record.read_text(encoding="utf-8") if record.is_file() else ""
    planned = {path for path, _source in PLANNED.findall(record_text)}
    questions = set(QUESTION.findall(record_text))
    if not record_text:
        problems.append(f"{record.name}: the lane record does not exist")

    # ---- every GAP row exactly once, and nothing else
    counted = collections.Counter(r["row"] for r in rows)
    for key, n in sorted(counted.items()):
        if n > 1:
            problems.append(f"{key}: {n} lines, want exactly one")
    for key in sorted(set(pop) - set(counted)):
        problems.append(f"{key}: a GAP row today with NO line -- nobody gave it a next step")
    for key in sorted(set(counted) - set(pop)):
        state = index.get(key, ("not a row",))[0]
        problems.append(f"{key}: has a line but is not a GAP row today ({state})")

    # ---- the count reconciles with the counter
    pinned_gap = cc.PINNED.get("gap")
    if len(rows) != len(pop):
        problems.append(f"the table has {len(rows)} lines and the walk {len(pop)} GAP rows")
    if pinned_gap is not None and len(pop) != pinned_gap:
        problems.append(f"the walk reads {len(pop)} GAP rows and census_completion pins {pinned_gap}")

    # ---- each line's own cells
    queue_ids = {q["surface-id"]: q for q in qrows}
    tracked = _tracked(root)
    is_read_url = _boundary()
    if is_read_url is None:
        not_checked.append("ADMIT addresses and queue verdicts: linkedin_server is not importable here")
    synthetic = []
    for r in rows:
        key = r["row"]
        letter = key.split(" ", 1)[0]
        if r["slice"] != letter:
            problems.append(f"{key}: slice {r['slice']!r}, its id says {letter!r}")
        want_dir = jd.get(key) if letter == "J" else pop.get(key, ("", ""))[1]
        if key in pop and r["dir"] != want_dir:
            problems.append(f"{key}: dir {r['dir']!r}, the census reads {want_dir!r}")
        if r["dir"] not in DIRECTIONS:
            problems.append(f"{key}: dir {r['dir']!r} is off {DIRECTIONS}")
        want_class = wclass.get(key, "-")
        if r["class"] != want_class:
            problems.append(f"{key}: class {r['class']!r}, the write-class table reads {want_class!r}")
        if r["basis"] not in BASES:
            problems.append(f"{key}: basis {r['basis']!r} is off {BASES}")
        kind, _, payload = r["next"].partition(":")
        if kind not in KINDS or not payload.strip():
            problems.append(f"{key}: next {r['next']!r} is not <KIND>:<payload> with KIND in {KINDS}")
            continue
        # sources: census keys here, every other form by the shipped resolver
        parts = [p.strip() for p in r["source"].split(" ; ") if p.strip()]
        if not parts:
            problems.append(f"{key}: no source named")
        rest = []
        for part in parts:
            if CENSUS_KEY.match(part):
                if part not in index:
                    problems.append(f"{key}: source {part} is not a census row")
            elif FIXTURE.match(part):
                # A captured page the step rests on. The shipped resolver reads
                # only .py/.md/.tsv/.json, so a fixture is resolved here: it
                # must be TRACKED, because an untracked one reaches no clone.
                if part not in tracked:
                    problems.append(f"{key}: source {part} is not a tracked fixture")
            else:
                rest.append(part)
        if rest:
            synthetic.append({"key": key, "sources": " ; ".join(rest)})
        # payloads
        if kind == "CAPTURE":
            line = queue_ids.get(payload)
            if line is None:
                problems.append(f"{key}: CAPTURE:{payload} has no line in the capture queue")
            elif key not in [x.strip() for x in line["rows"].split(",")]:
                problems.append(f"{key}: CAPTURE:{payload}'s queue line does not list this row")
        elif kind == "BUILD":
            if payload not in tracked and payload not in planned:
                problems.append(f"{key}: BUILD:{payload} is neither a tracked fixture nor PLANNED "
                                f"in {record.name}")
        elif kind == "RULING":
            if payload not in questions:
                problems.append(f"{key}: RULING:{payload} has no '### {payload}' question in {record.name}")
        elif kind == "SIBLING":
            if payload not in LANES and payload not in index:
                problems.append(f"{key}: SIBLING:{payload} is neither {LANES} nor a census row")
            if payload == key:
                problems.append(f"{key}: SIBLING of itself")
        elif kind == "ADMIT":
            if not payload.startswith("https://www.linkedin.com/"):
                problems.append(f"{key}: ADMIT:{payload} is not a linkedin.com address")
            elif is_read_url is not None and is_read_url(payload):
                problems.append(f"{key}: ADMIT:{payload} is already admitted -- the step is stale")
    problems += cwc.source_problems(synthetic, root)

    # ---- the queue
    by_key = {r["row"]: r for r in rows}
    ids = collections.Counter(q["surface-id"] for q in qrows)
    for sid, n in ids.items():
        if n > 1:
            problems.append(f"queue: surface {sid} has {n} lines")
    on_a_line: set[str] = set()
    for q in qrows:
        sid = q["surface-id"]
        members = [x.strip() for x in q["rows"].split(",") if x.strip()]
        if not members:
            problems.append(f"queue {sid}: unblocks no row")
        if str(len(members)) != q["rows_unblocked"]:
            problems.append(f"queue {sid}: rows_unblocked {q['rows_unblocked']} but {len(members)} rows listed")
        for member in members:
            on_a_line.add(member)
            if member not in index:
                problems.append(f"queue {sid}: {member} is not a census row")
                continue
            step = by_key.get(member, {}).get("next", "")
            needs = q["needs"]
            if needs == "-" and step != f"CAPTURE:{sid}":
                problems.append(f"queue {sid}: {member}'s step is {step!r}, not CAPTURE:{sid}")
            elif needs.startswith("TARGET") and not step.startswith("TARGET:"):
                problems.append(f"queue {sid}: {member}'s step is {step!r}, not a TARGET")
            elif needs.startswith("ADMIT") and step != f"ADMIT:{q['address']}":
                problems.append(f"queue {sid}: {member}'s step is {step!r}, not ADMIT:{q['address']}")
            elif needs.startswith("RULING: ") and step != "RULING:" + needs[len("RULING: "):]:
                problems.append(f"queue {sid}: {member}'s step is {step!r}, not {needs!r}")
        if is_read_url is not None:
            admitted = is_read_url(q["address"])
            if admitted != (q["address_verdict"] == "ADMITTED"):
                problems.append(f"queue {sid}: address_verdict {q['address_verdict'][:20]!r} but "
                                f"is_read_url reads {admitted}")
    for r in rows:
        kind = r["next"].split(":", 1)[0]
        if kind in ("CAPTURE", "TARGET", "ADMIT") and r["row"] not in on_a_line:
            problems.append(f"{r['row']}: {kind} row on no capture-queue line")
    not_checked.append("the press verdict text in the queue (re-driven by the generator, not here)")
    not_checked.append("the session cut (loads per session) -- the queue's own arithmetic")
    return rows, qrows, problems, not_checked


def summary(rows: list[dict]) -> list[str]:
    kinds = collections.Counter(r["next"].split(":", 1)[0] for r in rows)
    lanes = collections.Counter(r["next"] for r in rows if r["next"].startswith("SIBLING:lane"))
    bases = collections.Counter(r["basis"] for r in rows)
    out = [f"rows {len(rows)}"]
    out += [f"    {k:<13} {kinds[k]:>4}" for k in KINDS]
    out.append("    " + ", ".join(f"{k} {v}" for k, v in sorted(lanes.items())))
    out.append("    basis " + ", ".join(f"{k} {bases[k]}" for k in BASES))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--table", type=pathlib.Path, default=TABLE)
    ap.add_argument("--queue", type=pathlib.Path, default=QUEUE)
    ap.add_argument("--record", type=pathlib.Path, default=RECORD)
    args = ap.parse_args(argv)
    rows, qrows, problems, not_checked = check(args.table, args.queue, args.record)
    for line in summary(rows):
        print(line)
    print(f"queue lines {len(qrows)}")
    for line in not_checked:
        print(f"NOT CHECKED: {line}")
    if problems:
        print(f"\nRED: {len(problems)} problem(s)")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"GREEN: every GAP row once ({len(rows)} = census_completion's gap), "
          f"every source and payload resolving, the queue agreeing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
