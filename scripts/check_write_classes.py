"""Every write-direction still-GAP row, classed R1 / R2 / R3, and kept true.

THE QUESTION. The census holds 151 write-direction GAP rows at ``b0d3ab8``
(three slices; ``jobs.md`` has no direction column). The standing write design
builds writes in a SINGLE-USE GRANT MODEL, and the operator scoped its first
round to REVERSIBLE actions while cutting three others outright. A lane that
builds writes has to know, per row, which of those decisions governs it -- and
until this table that answer lived in nobody's column.

``_audit/_census/write-classes.tsv`` is that column. One line per row:

    R1  the sanctioned reversible first-round class -- save / unsave, follow /
        unfollow, the Open To Work signal
    R2  OUTWARD (WAS CUT; ALLOWED 2026-09-23 18:15) -- apply, connect, a
        message or InMail send. MEMBERSHIP is still defined by the operator's
        cut, which names the acts; their STATUS changed with WRITE-CLASS-B,
        his ruling (b), relayed to this lane mid-wave and registered on
        master at 53ba1b6 (the lane audit, section 5). Every R2 line carries
        BUILD-READY detail for the lane that builds it.
    R3  other, or undecided -- including rows ADJACENT to R1 whose membership
        is a reading nobody has made

THE R2 BUILD-READY COLUMNS. ``r2_action`` (what the write would be),
``r2_target`` (opening with one of :data:`WRITE_CLASS_R2_TARGETS`),
``r2_undo`` (whether it can be undone and how) and ``r2_live_proof`` (the
minimal live proof and the kind of target the operator must name). Required
on every R2 line, and ``-`` on every other line -- so detail cannot quietly
attach to a row nobody has cleared to build.

THE CLASS IS NOT TYPED, IT IS DERIVED FROM THE ACT. Every line names its act
from the closed vocabulary :data:`WRITE_CLASS_ACTS`, and the class is a property of the
act. A line whose class disagrees with its act is red, so widening R1 needs an
edit HERE -- where a reviewer sees the vocabulary move -- rather than one
quiet cell in a 151-line table.

THIS FILE EXITS 1 WHEN:

  * a write-direction GAP row has no line (a row ENTERED the population and
    nobody classed it), or a line names a row that is no longer in it and is
    not a row this lane BUILT (a row LEFT and its class points at nothing);
  * a line is duplicated, or breaks the column set, or is not ASCII;
  * a line's capability text no longer matches its census cell;
  * a class disagrees with its act, or an act is off the vocabulary;
  * a line does not cite its own census row, or an R1 / R2 line does not
    cite the passage that DEFINES its class, or any citation fails to resolve
    -- including a ruling the register now reads SUPERSEDED, which still
    resolves by id and no longer says anything that is true;
  * a ``built:`` line names an action that is not in ``writes.PERFORMABLE``,
    or whose row is still GAP -- or an R2 line carries a disposition (R3 may,
    since lane L7 took its profile-family rows to a build or a named queue);
  * an R2 line lacks any of its four build-ready columns, its target does not
    open with one of the four kinds, or a non-R2 line carries any of them.

THE WALK IS REPLICATED AND EVERY DECISION IN IT IS IMPORTED -- the same shape
``scripts/census_completion.py`` states for its own ``walk()``. The row filter,
``cells``, ``state_of`` and ``HEADERS`` are ``count_census_states``'s,
``ADMIN_ONLY`` is ``enumerate_gap_rows``'s and the direction is
``reader_closable_blockers.direction_of``. Only the loop is local, because this
table needs the CAPABILITY cell and neither shipped walk returns it.

THE IMPORT OF THE WRITE MODULE IS LAZY, and only the ``built:`` check needs it,
so the parse and the population stay pure.

SHOWN FAILING: ``tests/test_write_classes.py`` plants seventeen defects into
a COPY of the real table -- a missing row, a duplicate, a row that is not a
write-direction GAP row, a class disagreeing with its act, a CONSISTENT
widening (act and class rewritten together) that only the defining-passage
rule can see, an off-vocabulary act, a drifted capability, a missing
self-citation, a phrase that no longer resolves, a ruling id that is not
registered, a ruling the register reads SUPERSEDED, a build naming an action
that cannot perform, a classify-only
class carrying a build, an R2 line missing its build-ready detail, detail on
an R3 line, an R2 target outside the four kinds, and non-ASCII -- and asserts
each turns this red and names the row. It asserts green on the real table
too. A check that has only been seen passing certifies nothing.

WHAT IT DOES NOT CHECK, so its green is not read as more. WHICH ACT a
capability is -- ``follow`` for "Follow a skills Page", ``subscribe`` for
"Subscribe to a newsletter" -- is JUDGEMENT, and it is written into the
``ground`` column where it can be argued with. This file checks that the
judgement is consistent and cited, never that it is right.

    python scripts/check_write_classes.py
    python scripts/check_write_classes.py --table <a copy>   # for controls
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
_WC_SCRIPTS_DIR = ROOT / "scripts"
if str(_WC_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_WC_SCRIPTS_DIR))

import count_census_states as ccs  # noqa: E402  (the shipped counter)
import enumerate_gap_rows as egr  # noqa: E402  (the shipped enumerator)
import reader_closable_blockers as rcb  # noqa: E402  (the shipped direction finder)

WRITE_CLASS_TABLE = ROOT / "_audit" / "_census" / "write-classes.tsv"

WRITE_CLASS_COLUMNS = ("key", "capability", "act", "class", "disposition",
                       "ground", "sources", "r2_action", "r2_target",
                       "r2_undo", "r2_live_proof")

#: The four R2 build-ready columns, in table order.
WRITE_CLASS_R2_DETAIL = ("r2_action", "r2_target", "r2_undo", "r2_live_proof")

#: What an outward write lands on. ``r2_target`` must OPEN with one of these,
#: the four the orchestrator's note named, so the next lane can group by it.
WRITE_CLASS_R2_TARGETS = ("person", "thread", "job", "post")

WRITE_CLASS_NAMES = ("R1", "R2", "R3")

#: THE CLOSED ACT VOCABULARY, and the class each act carries. The class of a
#: line is DERIVED from this map; a line cannot state one the map disagrees
#: with. R1's acts are the first round's own verbs and nothing wider -- the
#: adjacent ones are R3 on purpose, and ``ground`` says why for each row.
WRITE_CLASS_ACTS: dict[str, str] = {
    # R1 -- the sanctioned reversible first round
    "save": "R1",
    "unsave": "R1",
    "follow": "R1",
    "unfollow": "R1",
    "follow-or-unfollow": "R1",
    "open-to-work": "R1",
    # R2 -- cut by the operator
    "apply": "R2",
    "connect": "R2",
    "message-send": "R2",
    # R3 -- other, or undecided
    "open-to-adjacent": "R3",
    "subscribe": "R3",
    "invite-others": "R3",
    "profile-edit": "R3",
    "profile-badge": "R3",
    "profile-setting": "R3",
    "endorsement-visibility": "R3",
    "services-page": "R3",
    "verification": "R3",
    "newsletter-author": "R3",
    "event": "R3",
    "group": "R3",
    "messaging-manage": "R3",
    "message-react": "R3",
    "report": "R3",
    "feed-curation": "R3",
    "publish": "R3",
    "upload": "R3",
    "comment": "R3",
    "comment-control": "R3",
    "react": "R3",
    "mention-control": "R3",
    "collaborative": "R3",
    "share": "R3",
    "admin-act": "R3",
    "filter-read": "R3",
    "notification-preference": "R3",
    # Added 2026-09-24 (lane Y2) for `N 198`: a helpful / not-helpful verdict sent
    # to LinkedIn itself about one of its surfaces. No act above names it -- a
    # `report` concerns content or a member, not whether a page helped. R3, the
    # residual class, so the first round's R1 is untouched.
    "feedback": "R3",
    # Added 2026-09-24 (lane Y2) for `P S9`: changing a paid plan. It spends money,
    # which no act above does; R3 because the operator's cut named no purchase,
    # and the row's own cell says a live proof of it needs him.
    "purchase": "R3",
}

#: The passage each non-residual class RESTS ON. A line of that class must cite
#: it verbatim, so the class cannot be asserted without its authority.
WRITE_CLASS_DEFINING: dict[str, str] = {
    "R1": ("_audit/_census/network.md::the first write round ships only "
           "reversible actions (save/unsave, follow, Open To Work)"),
    "R2": ("linkedin_server/writes.py::apply, connect and message/InMail were "
           "removed from the round"),
}

#: A row this lane built LEAVES the population, so it keeps its line only in
#: one of these states. Anything else is a row that moved for another reason.
WRITE_CLASS_BUILT_STATES = ("COVERED-UNFIRED", "COVERED-PROVEN")

#: KNOWN ANSWERS for the walk, so an empty or inverted population cannot pass
#: as agreement. ``M M6`` (send a message request) is a write-direction GAP
#: row; ``N 1`` is a COVERED-UNFIRED write and ``P A1`` is a read.
WRITE_CLASS_KNOWN_IN = ("M M6", "P A14", "N 4")
WRITE_CLASS_KNOWN_OUT = ("N 1", "P A1")

_WC_DISPOSITION_RX = re.compile(r"^(built:[a-z_]+|queued:[A-Z0-9][A-Z0-9-]*|classify-only)$")
#: A row id may be a RANGE, ``O6-O20``: `profile.md` collapses fifteen toggles
#: into that one row, and it entered the write-direction population with lane R
#: (2026-09-23). The range form still has to name a row that exists -- the
#: resolver below searches the census for it verbatim.
_WC_SELF_ROW_RX = re.compile(
    r"^(_audit/_census/[a-z\-]+\.md) row ([A-Za-z]*\d+(?:-[A-Za-z]*\d+)?)$")
_WC_PATH_RX = re.compile(r"^([A-Za-z0-9_.\-/]+\.(?:py|md|tsv|json))(?:::(.+))?$")
_WC_RULING_RX = re.compile(r"^RULING:([A-Z0-9][A-Z0-9\-]*)$")


def _normalised(text: str) -> str:
    return " ".join(text.split())


def walk(root: pathlib.Path = ROOT):
    """(key, state, direction, capability, slice file) for every stated row.

    The loop ``census_completion.walk()`` and ``reader_closable_blockers.main``
    both run, with every decision inside it imported. A state cell spelled in a
    dialect raises through ``ccs.state_of`` rather than dropping the row.
    """
    census = root / "_audit" / "_census"
    for letter, name in ccs.SLICES.items():
        path = census / name
        for line in path.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
            if not line.startswith("|"):
                continue
            c = ccs.cells(line)
            if len(c) < 3:
                continue
            if c[0] and set(c[0]) <= set("-: "):
                continue
            if not ccs.ROW.match(line) or c[0].lower() in ccs.HEADERS:
                continue
            st = ccs.state_of(c)
            if not st and letter == "N" and egr.ADMIN_ONLY.fullmatch(c[0]):
                st = "GAP"
            if not st:
                continue
            yield (f"{letter} {c[0]}", st, rcb.direction_of(c), c[1].strip(),
                   f"_audit/_census/{name}")


def census_index(root: pathlib.Path = ROOT) -> dict[str, tuple[str, str, str, str]]:
    """key -> (state, direction, capability, slice file), for every stated row."""
    return {k: (st, d, cap, f) for k, st, d, cap, f in walk(root)}


def population(index: dict[str, tuple[str, str, str, str]]) -> set[str]:
    """The write-direction still-GAP keys -- the rows this table classifies."""
    return {k for k, (st, d, _cap, _f) in index.items()
            if st == "GAP" and d == "W"}


def load(path: pathlib.Path = WRITE_CLASS_TABLE) -> tuple[list[dict[str, str]], list[str]]:
    """(rows, problems). Parses the table and nothing else.

    ``#`` lines are commentary. The first other line must be the header spelled
    exactly, so a column cannot be reordered under a reader.
    """
    rows: list[dict[str, str]] = []
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return rows, [f"{path.name}: the class table does not exist"]
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        return rows, [f"{path.name}: not ASCII ({exc.reason} at byte "
                      f"{exc.start})"]
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    if not lines or tuple(lines[0].split("\t")) != WRITE_CLASS_COLUMNS:
        return rows, [f"{path.name}: the header is not exactly "
                      f"{'<TAB>'.join(WRITE_CLASS_COLUMNS)}"]
    problems: list[str] = []
    for number, line in enumerate(lines[1:], start=2):
        cells = line.split("\t")
        if len(cells) != len(WRITE_CLASS_COLUMNS):
            problems.append(f"data line {number}: {len(cells)} cells, want "
                            f"{len(WRITE_CLASS_COLUMNS)}")
            continue
        rows.append(dict(zip(WRITE_CLASS_COLUMNS, cells)))
    return rows, problems


def citations(row: dict[str, str]) -> list[str]:
    return [part.strip() for part in row["sources"].split(" ; ") if part.strip()]


def coverage_problems(rows: list[dict[str, str]],
                      index: dict[str, tuple[str, str, str, str]]) -> list[str]:
    """Every population row exactly once; nothing else unless this lane built it.

    BOTH DIRECTIONS OF DRIFT. A MISSING line is a row that entered the
    population unclassed. An EXTRA line is a row that left it; the only
    departure this table accounts for is a BUILD, and that is checked in
    :func:`disposition_problems`.
    """
    problems: list[str] = []
    pop = population(index)
    counted = collections.Counter(r["key"] for r in rows)
    for k, n in sorted(counted.items()):
        if n > 1:
            problems.append(f"{k}: {n} lines, want exactly one")
    for k in sorted(pop - set(counted)):
        problems.append(f"{k}: a write-direction GAP row today with NO line "
                        f"in the table -- nobody has classed it")
    built = {r["key"] for r in rows if r["disposition"].startswith("built:")}
    for k in sorted(set(counted) - pop):
        if k in built:
            continue
        if k not in index:
            problems.append(f"{k}: has a line but is not a row of any slice")
        else:
            st, d, _cap, _f = index[k]
            problems.append(f"{k}: has a line but is not a write-direction "
                            f"GAP row today (state {st}, direction {d}) and "
                            f"was not built here -- its class points at "
                            f"nothing")
    return problems


def shape_problems(rows: list[dict[str, str]],
                   index: dict[str, tuple[str, str, str, str]]) -> list[str]:
    """Vocabulary, derivation, capability text, and the self-citation."""
    problems: list[str] = []
    for r in rows:
        tag = r["key"]
        act, cls = r["act"], r["class"]
        if cls not in WRITE_CLASS_NAMES:
            problems.append(f"{tag}: class {cls!r} is off {WRITE_CLASS_NAMES}")
        if act not in WRITE_CLASS_ACTS:
            problems.append(f"{tag}: act {act!r} is off the closed vocabulary")
        elif WRITE_CLASS_ACTS[act] != cls:
            problems.append(f"{tag}: act {act!r} is class {WRITE_CLASS_ACTS[act]}, and the "
                            f"line says {cls}")
        if not _WC_DISPOSITION_RX.match(r["disposition"]):
            problems.append(f"{tag}: disposition {r['disposition']!r} is not "
                            f"built:<action>, queued:<BLOCKER> or classify-only")
        # R3 MAY CARRY A DISPOSITION SINCE 2026-09-24 (lane L7), which took
        # its 36 profile-family rows to a build or a named queue. The checks
        # that make a disposition TRUE are unchanged and apply to R3 as to R1
        # (``disposition_problems``: a build must be performable and have left
        # GAP; a queued row must still be GAP). R2 stays classify-only here.
        elif cls == "R2" and r["disposition"] != "classify-only":
            problems.append(f"{tag}: {cls} is classify-only in this lane; it "
                            f"carries {r['disposition']!r}")
        elif cls == "R1" and r["disposition"] == "classify-only":
            problems.append(f"{tag}: R1 must say built: or queued:, not "
                            f"classify-only")
        if len(r["ground"].strip()) < 30:
            problems.append(f"{tag}: ground must say why, in a sentence")
        known = index.get(tag)
        if known is not None and _normalised(known[2]) != _normalised(r["capability"]):
            problems.append(f"{tag}: capability text no longer matches the "
                            f"census cell")
        cites = citations(r)
        if known is not None:
            letter, _, rid = tag.partition(" ")
            want = f"{known[3]} row {rid}"
            if want not in cites:
                problems.append(f"{tag}: does not cite its own census row "
                                f"({want})")
        if cls in WRITE_CLASS_DEFINING and WRITE_CLASS_DEFINING[cls] not in cites:
            problems.append(f"{tag}: {cls} must cite the passage that defines "
                            f"it: {WRITE_CLASS_DEFINING[cls]}")
        problems += _r2_detail_problems(r)
    return problems


def _r2_detail_problems(r: dict[str, str]) -> list[str]:
    """The build-ready columns: all four on an R2 line, none on any other."""
    tag, cls = r["key"], r["class"]
    problems: list[str] = []
    for column in WRITE_CLASS_R2_DETAIL:
        value = r.get(column, "").strip()
        if cls != "R2":
            if value != "-":
                problems.append(f"{tag}: {column} is for R2 lines only; a {cls} "
                                f"line carries '-'")
            continue
        if value == "-" or len(value) < 10:
            problems.append(f"{tag}: R2 needs build-ready {column}, in words "
                            f"the next lane can start from")
    if cls == "R2":
        target = r.get("r2_target", "").strip()
        if target != "-" and not target.startswith(WRITE_CLASS_R2_TARGETS):
            problems.append(f"{tag}: r2_target must open with one of "
                            f"{WRITE_CLASS_R2_TARGETS}")
    return problems


def _registered_rulings(root: pathlib.Path) -> set[str]:
    text = (root / "_audit" / "RULINGS.md").read_text(encoding="utf-8",
                                                     errors="replace")
    return set(re.findall(r"^\| `([A-Z0-9][A-Z0-9\-]*)` \|", text, re.M))


def superseded_rulings(root: pathlib.Path = ROOT) -> set[str]:
    """The registered rulings whose CLAIM cell opens ``SUPERSEDED``.

    A superseded ruling keeps its row in the register, so its id still
    resolves -- and that is the trap: a table citing it stays green while the
    thing it cites no longer holds. MEASURED at the lane-L4 merge: this table
    cited ``DO-NOT-OPEN-MESSAGING`` on 32 lines after ``WRITE-CLASS-B``
    superseded it, every check here passed, and this rule turned all 32 red
    before the table was regenerated. An AMENDED ruling is still in force in
    part and is not refused.
    """
    text = (root / "_audit" / "RULINGS.md").read_text(encoding="utf-8",
                                                     errors="replace")
    return set(re.findall(r"^\| `([A-Z0-9][A-Z0-9\-]*)` \| SUPERSEDED\b",
                          text, re.M))


def source_problems(rows: list[dict[str, str]],
                    root: pathlib.Path = ROOT) -> list[str]:
    """Every citation RESOLVES: the file, the phrase, the census row, the ruling.

    A citation here rots into a plausible wrong answer rather than a dangling
    one, so it is re-resolved on every run. A phrase is matched after
    whitespace is normalised on both sides, because the passages it quotes
    wrap across lines in their files.
    """
    problems: list[str] = []
    rulings = _registered_rulings(root)
    superseded = superseded_rulings(root)
    cache: dict[pathlib.Path, str] = {}

    def text_of(path: pathlib.Path) -> str:
        if path not in cache:
            cache[path] = _normalised(path.read_text(encoding="utf-8",
                                                     errors="replace"))
        return cache[path]

    for r in rows:
        tag = r["key"]
        cites = citations(r)
        if not cites:
            problems.append(f"{tag}: no source named")
        for cite in cites:
            ruling = _WC_RULING_RX.match(cite)
            if ruling:
                if ruling.group(1) not in rulings:
                    problems.append(f"{tag}: ruling {ruling.group(1)} is not "
                                    f"registered in _audit/RULINGS.md")
                elif ruling.group(1) in superseded:
                    problems.append(f"{tag}: ruling {ruling.group(1)} is "
                                    f"SUPERSEDED in _audit/RULINGS.md -- cite "
                                    f"the ruling that replaced it")
                continue
            self_row = _WC_SELF_ROW_RX.match(cite)
            if self_row:
                path = root / self_row.group(1)
                if not path.is_file():
                    problems.append(f"{tag}: census file {self_row.group(1)} "
                                    f"does not exist")
                    continue
                raw = path.read_text(encoding="utf-8", errors="replace")
                if not re.search(rf"(?m)^\|\s*{re.escape(self_row.group(2))}\s*\|",
                                 raw):
                    problems.append(f"{tag}: row {self_row.group(2)} is no "
                                    f"longer a row of {self_row.group(1)}")
                continue
            found = _WC_PATH_RX.match(cite)
            if not found:
                problems.append(f"{tag}: citation {cite!r} is neither a path, "
                                f"a path::phrase, a census row nor a RULING:")
                continue
            path = root / found.group(1)
            if not path.is_file():
                problems.append(f"{tag}: source file {found.group(1)} does not "
                                f"exist")
                continue
            phrase = found.group(2)
            if phrase and _normalised(phrase) not in text_of(path):
                problems.append(f"{tag}: phrase does not resolve in "
                                f"{found.group(1)}: {phrase!r}")
    return problems


def _performable() -> frozenset[str]:
    """``writes.PERFORMABLE``, imported on first use -- see the docstring."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from linkedin_server import writes

    return frozenset(writes.PERFORMABLE)


def disposition_problems(rows: list[dict[str, str]],
                         index: dict[str, tuple[str, str, str, str]],
                         performable: frozenset[str] | None = None) -> list[str]:
    """A ``built:`` line names a performable action AND its row left GAP; a
    ``queued:`` line's row is still a write-direction GAP row."""
    problems: list[str] = []
    pop = population(index)
    for r in rows:
        tag, disp = r["key"], r["disposition"]
        if disp.startswith("built:"):
            action = disp.split(":", 1)[1]
            if performable is None:
                performable = _performable()
            if action not in performable:
                problems.append(f"{tag}: built:{action} is not in "
                                f"writes.PERFORMABLE")
            known = index.get(tag)
            if known is None:
                problems.append(f"{tag}: built but not a row of any slice")
            elif known[0] not in WRITE_CLASS_BUILT_STATES:
                problems.append(f"{tag}: built:{action} but the census still "
                                f"reads {known[0]} -- a build that did not "
                                f"move its row")
        elif disp.startswith("queued:") and tag not in pop:
            problems.append(f"{tag}: queued, but it is no longer a "
                            f"write-direction GAP row")
    return problems


def control_problems(index: dict[str, tuple[str, str, str, str]]) -> list[str]:
    """The walk, seen answering both ways, before anything is compared."""
    pop = population(index)
    problems = [f"CONTROL: {k} is a write-direction GAP row and the walk "
                f"missed it" for k in WRITE_CLASS_KNOWN_IN if k not in pop]
    problems += [f"CONTROL: {k} is not a write-direction GAP row and the walk "
                 f"counted it" for k in WRITE_CLASS_KNOWN_OUT if k in pop]
    if len(pop) < 100:
        problems.append(f"CONTROL: the walk found only {len(pop)} "
                        f"write-direction GAP rows")
    return problems


def split(rows: list[dict[str, str]]) -> dict[str, int]:
    classes = collections.Counter(r["class"] for r in rows)
    out = {c: classes[c] for c in WRITE_CLASS_NAMES}
    out["R1:built"] = sum(1 for r in rows if r["class"] == "R1"
                          and r["disposition"].startswith("built:"))
    out["R1:queued"] = sum(1 for r in rows if r["class"] == "R1"
                           and r["disposition"].startswith("queued:"))
    out["rows"] = len(rows)
    return out


def check(table: pathlib.Path = WRITE_CLASS_TABLE, root: pathlib.Path = ROOT,
          performable: frozenset[str] | None = None) -> tuple[list[dict[str, str]], list[str]]:
    """(rows, problems) -- every check above, over one table."""
    rows, problems = load(table)
    index = census_index(root)
    problems += control_problems(index)
    problems += coverage_problems(rows, index)
    problems += shape_problems(rows, index)
    problems += source_problems(rows, root)
    problems += disposition_problems(rows, index, performable)
    return rows, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check the write-class table "
                                 "against the census it classifies.")
    ap.add_argument("--table", type=pathlib.Path, default=WRITE_CLASS_TABLE,
                    help="the table to check (default: the committed one)")
    args = ap.parse_args(argv)
    rows, problems = check(args.table)
    pop = population(census_index())
    s = split(rows)
    print(f"write-direction GAP rows today {len(pop):4d}   the shipped walk")
    print(f"lines in the table             {len(rows):4d}   {args.table.name}")
    for c in WRITE_CLASS_NAMES:
        print(f"    {c}  {s[c]:4d}")
    print(f"    R1 built {s['R1:built']}, queued {s['R1:queued']}")
    if problems:
        print(f"RED: {len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"GREEN: {len(rows)} lines, every class derived from its act and "
          f"every citation resolving")
    return 0


if __name__ == "__main__":
    sys.exit(main())
