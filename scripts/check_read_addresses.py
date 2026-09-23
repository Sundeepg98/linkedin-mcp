"""Bucket 3, per row: does the SHIPPED read boundary admit the page each row needs?

THE QUESTION. ``scripts/census_completion.py`` calls its bucket 3 "blocked on
nothing at all" -- every read-direction still-GAP row -- and says in the same
breath that the figure is an UPPER BOUND, because nobody had run each row's page
ADDRESS through ``readonly.is_read_url``. The census records an address in
prose, never in a column, so no instrument could take that measurement.

``_audit/_census/read-addresses.tsv`` is that column: one line per bucket-3
row, the address, where it came from, the boundary's verdict, and a class. This
file keeps the column TRUE. It re-drives every recorded address through the
shipped boundary and exits 1 when:

  * a recorded ``is_read_url`` verdict disagrees with the live boundary;
  * a recorded refusal KIND disagrees with the refusal the boundary raises;
  * an ``also_driven`` address's recorded verdict disagrees;
  * a bucket-3 row has no line (a row ENTERED the bucket and nobody measured
    it), or a line names a row that is no longer in the bucket (a row LEFT and
    its verdict was left behind pointing at nothing -- the failure that has
    kept ``scripts/triage_read_gap_rows.py`` red at HEAD);
  * a row's direction cell moved, or a line breaks the table's vocabulary.

THE BOUNDARY IS IMPORTED, NEVER RE-IMPLEMENTED. The verdict is
``readonly.is_read_url(address)``. The refusal KIND is read off the exception
``readonly.assert_read_url`` raises -- the same message two committed tests in
``tests/test_readonly.py`` pin, telling a forbidden substring from allowlist
silence -- so this file parses the gate's own sentence and never re-derives
the patterns. ``_audit/2026-09-19-the-read-rows.md`` measured what a grep of
the pattern source costs: it found 24 patterns and 11 substrings where the
module held 32 and 33.

AND THE IMPORT IS LAZY, deliberately. ``census_completion.py`` imports this
module to count the class column, and ``scripts/_check_census_completion_can_
fail.py`` runs that instrument inside a copy of ``scripts/`` and ``_audit/
_census/`` that carries no ``linkedin_server`` package at all. So everything
that needs the boundary imports it inside the function that needs it, and
``load`` / ``coverage_problems`` / ``shape_problems`` / ``split`` stay pure.

SHOWN FAILING: ``tests/test_read_addresses.py`` plants a wrong verdict, a
missing row, a stale row, a wrong refusal kind, a wrong ``also_driven``
verdict, a class that contradicts its verdict and an off-alphabet gate, each
into a COPY of the real table, and asserts each turns this red and names the
row. It also asserts green on the real table. A check that has only ever been
seen passing certifies nothing.

WHAT IT DOES NOT CHECK, stated so its green is not read as more. The
JUDGEMENT columns -- which address is the row's page, the class of a row with
no address, the gate past an admitted boundary -- are checked for vocabulary
and consistency only. Nothing offline can check that an address is the one
LinkedIn serves: ALLOWED IS NOT SERVED, and ``/in/me/details/interests/`` is
this repository's standing proof (admitted, and it redirects).

    python scripts/check_read_addresses.py
    python scripts/check_read_addresses.py --table <a copy>   # for controls
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TABLE = ROOT / "_audit" / "_census" / "read-addresses.tsv"

COLUMNS = ("slice", "row", "dir", "class", "address", "basis", "source_kind",
           "source", "is_read_url", "refusal", "gate", "also_driven", "note")

#: The five classes. The first two carry an address the boundary was asked
#: about; the other three carry none, and say why in their note.
CLASSES = ("ADMITTED", "REFUSED", "NO-ADDRESS", "NEEDS-SESSION", "UNDETERMINED")
WITH_ADDRESS = ("ADMITTED", "REFUSED")
BASES = ("MEASURED", "NAMED", "INFERRED")
SOURCE_KINDS = ("code-symbol", "test-fixture", "census-prose", "prior-audit")

#: The first thing past an ADMITTED boundary, in the order a reader wave meets
#: them. The definitions live in `_audit/2026-09-23-bucket3-addresses.md`.
GATES = ("READER", "PRESS-PERMITTED", "MEASURE", "BUILT-UNFIRED", "PRESS",
         "RULING")

#: A reader could be written TODAY for these: no ruling, no boundary edit, and
#: no press the shipped gate refuses. This is the measured size of "blocked on
#: nothing at all" -- ADMITTED rows whose gate is one of these.
BLOCKED_ON_NOTHING = ("READER", "PRESS-PERMITTED")

#: Bucket 3 is census_completion's R + R+W still-GAP set; nothing else.
DIRECTIONS = ("R", "R+W")

HOST = "https://www.linkedin.com/"

#: THE BOUNDARY MUST BE SEEN TO SAY BOTH WORDS before its agreement with the
#: table means anything: a gate mutated into admit-everything or
#: refuse-everything would agree with half the rows and look like drift in the
#: other half. The feed root has been admitted since the first commit; a third
#: party's profile is the boundary's sharpest standing refusal.
MUST_ADMIT = (HOST + "feed/",)
MUST_REFUSE = (HOST + "in/someone-else/",)

_FORBIDDEN = re.compile(r" contains '([^']+)', which is not a read surface")


def load(path: pathlib.Path = TABLE) -> tuple[list[dict[str, str]], list[str]]:
    """(rows, problems). Parses the table and does nothing else.

    ``#`` lines are commentary. The first other line must be the column header,
    spelled exactly, so a column cannot be silently reordered under a reader.
    """
    rows: list[dict[str, str]] = []
    problems: list[str] = []
    try:
        text = path.read_text(encoding="ascii")
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


def population() -> dict[tuple[str, str], str]:
    """(slice, row id) -> direction for every bucket-3 row, today.

    TAKEN FROM ``census_completion.walk()``, the walk that prints the 67, so
    this table can never be checked against a different population from the
    one the completion figure is computed over. Imported here rather than at
    module level because ``census_completion`` imports THIS module.
    """
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import census_completion as cc

    return {(letter, rid): direction
            for letter, rid, state, direction in cc.walk()
            if state == "GAP" and direction in DIRECTIONS}


def coverage_problems(rows: list[dict[str, str]],
                      pop: dict[tuple[str, str], str]) -> list[str]:
    """Every bucket-3 row exactly once, nothing else, directions agreeing.

    BOTH DIRECTIONS OF DRIFT ARE CHECKED. A MISSING line is a row that entered
    the bucket and was never measured. An EXTRA line is a row that left it --
    banked, re-ruled, or its direction cell corrected -- and whose verdict now
    points at nothing; a check that only catches the first kind decays into
    the second without a sound.
    """
    problems: list[str] = []
    counted = collections.Counter(key(r) for r in rows)
    for k, n in sorted(counted.items()):
        if n > 1:
            problems.append(f"{k[0]} {k[1]}: {n} lines, want exactly one")
    for k in sorted(set(pop) - set(counted)):
        problems.append(f"{k[0]} {k[1]}: a bucket-3 row today (direction "
                        f"{pop[k]}) with NO line in the table -- nobody has "
                        f"measured its address")
    for k in sorted(set(counted) - set(pop)):
        problems.append(f"{k[0]} {k[1]}: has a line but is NOT a bucket-3 row "
                        f"today -- it left the bucket and its verdict points "
                        f"at nothing")
    for r in rows:
        want = pop.get(key(r))
        if want is not None and r["dir"] != want:
            problems.append(f"{r['slice']} {r['row']}: dir {r['dir']!r} but "
                            f"the census cell now reads {want!r}")
    return problems


def shape_problems(rows: list[dict[str, str]]) -> list[str]:
    """The vocabulary, and the consistency a reader of each column relies on."""
    problems: list[str] = []
    for r in rows:
        tag = f"{r['slice']} {r['row']}"
        cls = r["class"]
        if cls not in CLASSES:
            problems.append(f"{tag}: class {cls!r} is off the alphabet {CLASSES}")
            continue
        if r["source_kind"] not in SOURCE_KINDS:
            problems.append(f"{tag}: source_kind {r['source_kind']!r} is off "
                            f"{SOURCE_KINDS}")
        if not r["source"].strip() or r["source"] == "-":
            problems.append(f"{tag}: no source named")
        if cls in WITH_ADDRESS:
            if not r["address"].startswith(HOST):
                problems.append(f"{tag}: {cls} needs an absolute address on "
                                f"{HOST}")
            if r["basis"] not in BASES:
                problems.append(f"{tag}: basis {r['basis']!r} is off {BASES}")
            if r["is_read_url"] not in ("True", "False"):
                problems.append(f"{tag}: is_read_url {r['is_read_url']!r} is "
                                f"not True or False")
            elif (r["is_read_url"] == "True") != (cls == "ADMITTED"):
                problems.append(f"{tag}: class {cls} contradicts its own "
                                f"recorded verdict is_read_url="
                                f"{r['is_read_url']}")
        else:
            for column in ("address", "basis", "is_read_url", "refusal"):
                if r[column] != "-":
                    problems.append(f"{tag}: {cls} carries no address, so "
                                    f"{column} must be '-'")
            if len(r["note"].strip()) < 40:
                problems.append(f"{tag}: {cls} must say in its note what it "
                                f"derives from or what is unknown")
        if cls == "ADMITTED":
            if r["gate"] not in GATES:
                problems.append(f"{tag}: gate {r['gate']!r} is off {GATES}")
        elif r["gate"] != "n/a":
            problems.append(f"{tag}: gate is for ADMITTED rows only; {cls} "
                            f"carries {r['gate']!r}")
        if r["gate"] not in ("READER", "n/a") and len(r["note"].strip()) < 40:
            problems.append(f"{tag}: gate {r['gate']} must say in its note "
                            f"what it rests on")
        for url, _verdict in _also(r):
            if not url.startswith(HOST):
                problems.append(f"{tag}: also_driven entry {url!r} is not an "
                                f"absolute address on {HOST}")
        if r["also_driven"] != "-" and not _also(r):
            problems.append(f"{tag}: also_driven is neither '-' nor "
                            f"'<address>=><verdict> ; ...'")
    return problems


def _also(row: dict[str, str]) -> list[tuple[str, str]]:
    if row["also_driven"] == "-":
        return []
    out = []
    for part in row["also_driven"].split(" ; "):
        url, sep, verdict = part.partition("=>")
        if sep:
            out.append((url, verdict))
    return out


def kind_of_refusal(message: str) -> str:
    """The refusal's KIND, read off the shipped gate's own sentence.

    Never empty and never a bare word that could pass for a verdict: a message
    this cannot place comes back as ``UNREADABLE`` and fails the comparison,
    so a reworded gate is reported rather than matched by accident.
    """
    hit = _FORBIDDEN.search(message)
    if hit:
        if "A READ PATTERN DOES ADMIT THIS ADDRESS" in message:
            return f"FORBIDDEN[{hit.group(1)}]+PATTERN-WOULD-ADMIT"
        if "AND NO READ PATTERN ADMITS THIS ADDRESS EITHER" in message:
            return f"FORBIDDEN[{hit.group(1)}]+NO-PATTERN"
        return f"FORBIDDEN[{hit.group(1)}]+UNREADABLE"
    if "is not on the read-only allowlist" in message:
        return "NO-PATTERN"
    return "UNREADABLE"


def _boundary():
    """The shipped read boundary, imported on first use -- see the docstring."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from linkedin_server import readonly

    return readonly


def refusal_of(url: str) -> str:
    """``-`` if the shipped boundary admits ``url``, else its refusal kind."""
    readonly = _boundary()
    try:
        readonly.assert_read_url(url)
    except readonly.WriteAttemptError as exc:
        return kind_of_refusal(str(exc))
    return "-"


def control_problems() -> list[str]:
    """The boundary, seen saying BOTH words, before anything is compared."""
    readonly = _boundary()
    problems: list[str] = []
    for url in MUST_ADMIT:
        if readonly.is_read_url(url) is not True:
            problems.append(f"CONTROL: the boundary refuses {url}, which it "
                            f"has admitted since the first commit")
    for url in MUST_REFUSE:
        if readonly.is_read_url(url) is not False:
            problems.append(f"CONTROL: the boundary admits {url}, a third "
                            f"party's profile")
    return problems


def boundary_problems(rows: list[dict[str, str]]) -> list[str]:
    """Every recorded verdict and refusal kind against the LIVE boundary."""
    readonly = _boundary()
    problems: list[str] = []
    for r in rows:
        tag = f"{r['slice']} {r['row']}"
        if r["class"] in WITH_ADDRESS and r["address"].startswith(HOST):
            live = readonly.is_read_url(r["address"])
            if str(live) != r["is_read_url"]:
                problems.append(f"{tag}: recorded is_read_url="
                                f"{r['is_read_url']}, the live boundary says "
                                f"{live} for {r['address']}")
            kind = refusal_of(r["address"])
            if kind != r["refusal"]:
                problems.append(f"{tag}: recorded refusal {r['refusal']!r}, "
                                f"the live boundary raises {kind!r}")
        for url, verdict in _also(r):
            if url.startswith(HOST):
                live = readonly.is_read_url(url)
                if str(live) != verdict:
                    problems.append(f"{tag}: also_driven {url} recorded "
                                    f"{verdict}, the live boundary says {live}")
    return problems


def split(rows: list[dict[str, str]]) -> dict[str, int]:
    """The measured decomposition, counted off the class and gate columns."""
    classes = collections.Counter(r["class"] for r in rows)
    gates = collections.Counter(r["gate"] for r in rows
                                if r["class"] == "ADMITTED")
    forbidden = sum(1 for r in rows if r["class"] == "REFUSED"
                    and r["refusal"].startswith("FORBIDDEN["))
    out = {f"class:{c}": classes[c] for c in CLASSES}
    out.update({f"gate:{g}": gates[g] for g in GATES})
    out["refused:forbidden"] = forbidden
    out["refused:no_pattern"] = classes["REFUSED"] - forbidden
    out["blocked_on_nothing"] = sum(gates[g] for g in BLOCKED_ON_NOTHING)
    out["rows"] = len(rows)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Re-drive bucket 3's addresses "
                                 "through the shipped read boundary.")
    ap.add_argument("--table", type=pathlib.Path, default=TABLE,
                    help="the table to check (default: the committed one)")
    args = ap.parse_args(argv)

    rows, problems = load(args.table)
    pop = population()
    problems += coverage_problems(rows, pop)
    problems += shape_problems(rows)
    problems += control_problems()
    problems += boundary_problems(rows)

    driven = sum(1 for r in rows if r["class"] in WITH_ADDRESS)
    also = sum(len(_also(r)) for r in rows)
    print(f"bucket-3 rows today            {len(pop):4d}   census_completion.walk()")
    print(f"lines in the table             {len(rows):4d}   {args.table.name}")
    print(f"addresses re-driven            {driven:4d}   + {also} also_driven")
    s = split(rows)
    print()
    for c in CLASSES:
        print(f"    {c:16s} {s['class:' + c]:4d}")
    print(f"      REFUSED by a forbidden substring {s['refused:forbidden']}, "
          f"by allowlist silence {s['refused:no_pattern']}")
    print()
    print("    of the ADMITTED, the first thing past the boundary:")
    for g in GATES:
        print(f"      {g:16s} {s['gate:' + g]:4d}")
    print(f"    BLOCKED ON NOTHING           {s['blocked_on_nothing']:4d}   "
          f"ADMITTED and gate in {BLOCKED_ON_NOTHING}")
    print()
    if problems:
        print(f"RED: {len(problems)} problem(s). The table no longer describes "
              f"the tree:")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"GREEN: {len(rows)} of {len(pop)} bucket-3 rows, every recorded "
          f"verdict agrees with the live boundary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
