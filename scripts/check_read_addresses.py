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
    its verdict was left behind pointing at nothing -- the failure that kept
    ``scripts/triage_read_gap_rows.py`` red at HEAD until 2026-09-23);
  * a row's direction cell moved, or a line breaks the table's vocabulary;
  * a row is classed BLOCKED ON NOTHING on a page a RULING holds -- the edge
    this table first shipped without (``ruling_problems``, below).

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
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import ruling_holds as rh  # noqa: E402  -- pure at import, see its docstring

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
#:
#: `STANDING-RULING` was added 2026-09-23 (`_audit/2026-09-23-census-cleanup.md`
#: item 6), and NOT folded into `RULING`, because the two send a reader to
#: different places. `RULING` is a decision nobody has made -- it belongs in
#: the operator's open queue. `STANDING-RULING` is one he HAS made and that is
#: in force (the row's note cites it with HELD BY): nothing past the boundary
#: is reachable before it, and filing it as `RULING` would put a decided
#: question back into the open queue. No row carries it since the operator
#: lifted `DO-NOT-OPEN-MESSAGING` at 18:15 that day; `M M49` carried it until
#: then. It stays in the alphabet for the next ruling that holds a page.
GATES = ("READER", "PRESS-PERMITTED", "MEASURE", "BUILT-UNFIRED", "PRESS",
         "RULING", "STANDING-RULING")

#: A reader could be written TODAY for these: no ruling made or pending holds
#: the page, no boundary edit, and no press the shipped gate refuses. This is
#: the measured size of "blocked on nothing at all" -- ADMITTED rows whose gate
#: is one of these. `ruling_problems` refuses the table if one of them sits on
#: a page a ruling holds.
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
    except FileNotFoundError:
        # A PROBLEM, NEVER AN EMPTY TABLE: zero rows would read as zero
        # coverage for a reason nobody could see.
        return rows, [f"{path.name}: the address table does not exist at "
                      f"{path.parent.name}/{path.name}"]
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
    here = str(pathlib.Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
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
            if (r["refusal"] == "-") != (cls == "ADMITTED"):
                problems.append(f"{tag}: class {cls} contradicts its own "
                                f"recorded refusal {r['refusal']!r}")
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


_SOURCE_PATH = re.compile(r"^([A-Za-z0-9_.\-/]+\.(?:py|md|tsv|json))(?:::([A-Za-z_][A-Za-z0-9_]*))?")
_SOURCE_ROW = re.compile(r"\brow ([A-Za-z]*\d+[a-z]?)\b")


def source_problems(rows: list[dict[str, str]],
                    root: pathlib.Path = ROOT) -> list[str]:
    """Every row's source still RESOLVES: the file, the symbol, the census row.

    A citation in this repository does not rot into a dangling reference; it
    rots into a plausible wrong answer. So the source column is checked the
    way the verdict column is, on every run: the path must exist, a
    ``::SYMBOL`` must still be spelled in that file, and ``<census slice> row
    <id>`` must still be a row of that slice.

    KEPT OUT OF ``shape_problems`` on purpose, because ``census_completion.py``
    calls that one inside a copy of the tree that carries only ``scripts/`` and
    ``_audit/_census/`` -- where most sources legitimately do not exist.
    """
    problems: list[str] = []
    for r in rows:
        tag = f"{r['slice']} {r['row']}"
        found = _SOURCE_PATH.match(r["source"])
        if not found:
            problems.append(f"{tag}: source {r['source']!r} does not open on a "
                            f"repository path")
            continue
        path = root / found.group(1)
        if not path.is_file():
            problems.append(f"{tag}: source file {found.group(1)} does not "
                            f"exist")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        symbol = found.group(2)
        if symbol and not re.search(rf"\b{re.escape(symbol)}\b", text):
            problems.append(f"{tag}: source symbol {symbol} is no longer "
                            f"spelled in {found.group(1)}")
        cited = _SOURCE_ROW.search(r["source"])
        if cited and found.group(1).startswith("_audit/_census/"):
            if not re.search(rf"(?m)^\|\s*{re.escape(cited.group(1))}\s*\|",
                             text):
                problems.append(f"{tag}: source row {cited.group(1)} is no "
                                f"longer a row of {found.group(1)}")
    return problems


def ruling_problems(rows: list[dict[str, str]]) -> list[str]:
    """No row is blocked on nothing on a page a RULING holds.

    THE EDGE THIS TABLE SHIPPED WITHOUT, measured 2026-09-23. ``M M49`` was
    classed READER -- blocked on nothing -- because the shipped boundary admits
    ``/messaging/thread/<id>/``, while ``DO-NOT-OPEN-MESSAGING`` forbade
    opening messaging at all. The boundary says what the CODE may open; a
    ruling says what may be DONE; the split asked only the first. Nothing in
    the table's own vocabulary could see it, because the row was internally
    consistent. Run on the table as it then stood, this edge named ``M M49``
    and nothing else.

    AND THE SAME DAY THE ANSWER MOVED: the operator lifted that ruling at 18:15
    (his ruling (b), relayed), so ``M M49`` is READER again and the edge is
    green on it -- because it reads the holds as they are NOW, from one table.
    A split that had typed "held" into the row would now be the stale one.

    Every ADMITTED row's page is looked up among the holds in
    ``ruling_holds.ROW_HOLDS`` that bind a SURFACE. A hold that binds an ACT --
    the one on every write -- cannot be read off an address, so a row held that
    way must say so in its note, and nothing here can check it. On a held page:

      * a BLOCKED-ON-NOTHING gate is RED -- the edge itself;
      * a STANDING hold with any gate but STANDING-RULING is RED: nothing past
        the boundary is reachable before a ruling in force;
      * a PENDING hold with any gate but RULING is RED: the open question comes
        first, and it is a decision nobody has made;
      * a note that does not cite the hold with ``HELD BY`` is RED, so the
        table says WHICH ruling in the row a reader will open.

    And the converse, so the new gate cannot be spent carelessly: a
    STANDING-RULING row must cite a STANDING hold, and when that hold binds a
    surface the row's page must sit on it. And on ANY row, a note still citing
    a LIFTED ruling with ``HELD BY`` is RED: that citation is history.

    PURE: the holds table is imported, the register is not. That it still
    agrees with the register is ``ruling_holds.register_problems``, which
    ``main`` runs and ``census_completion.py`` cannot.
    """
    problems: list[str] = []
    for r in rows:
        for lifted in (c for c in rh.cited(r["note"])
                       if c in rh.LIFTED_ROW_HOLDS):
            problems.append(f"{r['slice']} {r['row']}: its note cites HELD BY "
                            f"`{lifted}`, and that ruling is lifted -- "
                            f"{rh.LIFTED_ROW_HOLDS[lifted]}")
        if r["class"] != "ADMITTED" or not r["address"].startswith(HOST):
            continue
        tag = f"{r['slice']} {r['row']}"
        path = urllib.parse.urlsplit(r["address"]).path
        gate = r["gate"]
        cites = rh.cited(r["note"])
        held = rh.surface_hold(path)
        if held is not None:
            hold = rh.ROW_HOLDS[held]
            if gate in BLOCKED_ON_NOTHING:
                problems.append(f"{tag}: classed blocked on nothing (gate "
                                f"{gate}), but its page {path} sits on "
                                f"{hold.surface}, which {held} holds "
                                f"({hold.status})")
            elif hold.status == "STANDING" and gate != "STANDING-RULING":
                problems.append(f"{tag}: gate {gate}, but {held} (STANDING) "
                                f"holds its page {path} before anything past "
                                f"the boundary -- the gate is STANDING-RULING")
            elif hold.status == "PENDING" and gate != "RULING":
                problems.append(f"{tag}: gate {gate}, but its page {path} "
                                f"waits on the open question {held} first -- "
                                f"the gate is RULING")
            if held not in cites:
                problems.append(f"{tag}: its page sits on {hold.surface}, so "
                                f"its note must cite HELD BY `{held}`")
        if gate == "STANDING-RULING":
            standing = [c for c in cites
                        if c in rh.ROW_HOLDS
                        and rh.ROW_HOLDS[c].status == "STANDING"]
            if not standing:
                problems.append(f"{tag}: gate STANDING-RULING, and its note "
                                f"cites no STANDING hold with HELD BY")
            for c in standing:
                hold = rh.ROW_HOLDS[c]
                if hold.binds == "surface" and not path.startswith(hold.surface):
                    problems.append(f"{tag}: gate STANDING-RULING citing {c}, "
                                    f"but its page {path} is not on "
                                    f"{hold.surface}")
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
    problems += source_problems(rows)
    problems += ruling_problems(rows)
    problems += [f"HOLDS TABLE: {p}" for p in rh.register_problems()]
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
