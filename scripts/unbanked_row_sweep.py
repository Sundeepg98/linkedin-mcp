"""A FAILED INSTRUMENT, KEPT SO NOBODY BUILDS IT AGAIN. Do not trust its output.

**IT REFUSES TO RUN.** Its own controls convict it, and that refusal IS the
deliverable. Four designs were tried against the same known-answer test and all
four failed. If you are about to write a sweep that finds "rows already built
but still filed GAP", read this first -- it will cost you an hour otherwise.

THE PROBLEM IS REAL. A row leaves GAP only when somebody EDITS THE CENSUS.
Shipping a tool does not move it, making a ruling does not move it, measuring
the surface does not move it. Measured instances, all found BY HAND:

    J 9, J 11, J 12, J 13, J 14   shipped 2026-09-04, filed GAP until 09-19
    M C60, N 173                  tool shipped + fired live, filed GAP
    N 165                         ruled out by name in readonly.py, filed GAP
    J 10, K10                     found independently by a sibling wave

Eight in one cluster of twenty-four. The problem is worth solving. **This file
is the record that a text heuristic does not solve it.**

=============================================================================
FOUR DESIGNS, FOUR FAILURES, EACH CAUGHT BY A CONTROL
=============================================================================

**1. CELL-TEXT SIGNALS** -- scan the census cell for SHIPPED / BUILT / a cited
ruling. Found **0 of 7** known answers, and the cause is fatal to the whole
approach: before those rows were banked their cells read
``| 9 | Filter: Easy Apply only | a507441 | GAP | -- |``. **THE CELL SAYS
NOTHING, BECAUSE THE CENSUS NOT KNOWING THE WORK HAPPENED IS THE DEFECT
ITSELF.** A census-text scan can only find rows where somebody wrote the
evidence in and then forgot the state column.

**2. IDENTIFIER MATCHING** against the source -- adjacent capability words
joined into a snake_case form. Found **1 of 7**, and that one was a FALSE
match: "Filter: Easy Apply only" hit ``linkedin_apply_job``, the wrong tool,
on the word "apply".

**3. PARAMETER MATCHING** -- the signal that really serves those rows is a
tool PARAMETER (``easy_apply``, ``job_type``, ``in_your_network``). Found
**7 of 7** and looked like success. **IT WAS PASSING BY COINCIDENCE**, and a
match-quality control -- does the hit name the thing that ACTUALLY serves the
row? -- convicted it:

    J 11: wanted job_type,             got message_filter on linkedin_open_messaging
    J 12: wanted under_ten_applicants, got message_filter on linkedin_open_messaging
    J 13: wanted in_your_network,      got message_filter on linkedin_open_messaging

Three different job-search rows, all matched to a MESSAGING tool, all on the
word "filter". **A POSITIVE CONTROL THAT COUNTS HITS AND NOT THEIR CONTENT CAN
BE SATISFIED ENTIRELY BY COINCIDENCE**, and this one was, for three of five.

**4. SELF-CONTRADICTION** -- a GAP row whose own cell says RETIRED / RE-FILED /
COVERED-PROVEN. Needs no semantics and is the only one that nearly works. It
found **9 candidates and 0 genuine ones.** Every hit was a cell referring to
some OTHER row closure ("eleven of fourteen rows retired"; "composes with row
52, the one COVERED-PROVEN read in the slice") or announcing its own RE-FILE,
which changes a row blocker and not its state. Same cross-row contamination the
correction guard has -- prose about a neighbour reads as a claim about
yourself -- and five of the nine were caused by prose this wave wrote hours
earlier.

=============================================================================
WHY THERE IS NO FIFTH DESIGN
=============================================================================

The evidence linking "Filter: Easy Apply only" to ``f_AL`` is SEMANTIC. No
token overlap expresses it: "Filter: Under 10 applicants" and
``under_ten_applicants`` share one stemmed word, and so do a dozen unrelated
pairs. Raising the threshold loses J 11, J 12 and J 13; lowering it admits the
whole census.

**THE DURABLE FIX IS NOT A DETECTOR, IT IS A DISCIPLINE.** Do not hunt the
backlog with a heuristic; stop the backlog growing. Either bank the row in the
same commit that ships the capability, or add a guard that fails when a tool
gains a parameter and no census row moves with it. For the backlog that already
exists, the only method that has produced a correct answer is a HUMAN
cross-reference of the 42 tools against the GAP rows -- every one of the ten
instances above was found by a person reading the tree, none by a machine.

Run it if you want to watch it refuse::

    ./venv/Scripts/python.exe scripts/unbanked_row_sweep.py --control
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import enumerate_gap_rows as egr  # noqa: E402

ROOT = HERE.parent
SERVER = ROOT / "linkedin_server" / "server.py"
SOURCE = "\n".join(
    p.read_text(encoding="utf-8", errors="replace")
    for p in sorted((ROOT / "linkedin_server").glob("*.py"))
)

#: The commit BEFORE this wave banked the eight rows it verified by hand.
CONTROL_REF = "bab9538^"
#: Rows that were GAP at CONTROL_REF and are known-unbanked. Verified against
#: the source and the suite, not against a progress file.
CONTROL_MUST_FLAG = ("J 9", "J 11", "J 12", "J 13", "J 14", "M C60", "N 173")
#: Honestly-GAP rows at the same ref: no tool, no ruling, no measurement.
#: N 174 -- a surface that may not exist and a zero cannot settle.
#: N 161 -- search for groups, refused address, never measured.
CONTROL_MUST_NOT_FLAG = ("N 174", "N 161")

#: **THE CONTROL THAT CONVICTS THIS FILE.** Flagging a known-unbanked row is
#: not enough -- the MATCH must be the one that actually serves it. Without
#: this, the sweep passes by coincidence: "Filter: Employment type / job type"
#: matched ``message_filter on linkedin_open_messaging`` purely on the word
#: "filter", and counted as a hit for a row really served by ``job_type``.
CONTROL_EXPECTED_MATCH = {
    "J 9": "easy_apply",
    "J 11": "job_type",
    "J 12": "under_ten_applicants",
    "J 13": "in_your_network",
    "J 14": "fair_chance_employer",
}

ABSENT_SIGNAL = "Zqxjvbnm Unbanked Signal"

CITES_CODE = re.compile(r"`?(?:server|readonly|writes|dom|shape|groups)\.py:\d+")
CITES_RULING = re.compile(r"_audit/[0-9A-Za-z._/-]+\.md")
SAYS_SHIPPED = re.compile(
    r"\bSHIPPED\b|\bBUILT\b|\balready (?:built|shipped|exists|covered)\b"
    r"|\bis now (?:built|shipped)\b", re.IGNORECASE)
CONTRADICTS = re.compile(r"\bRETIRED\b|\bRE-FILED\b")


def registered_tools() -> frozenset[str]:
    """Tool names read off the server source, not guessed from a pattern."""
    text = SERVER.read_text(encoding="utf-8", errors="replace")
    return frozenset(re.findall(r"async def (linkedin_[a-z0-9_]+)", text))


TOOLS = registered_tools()


STOP = frozenset("""a an and are as at be by for from her his in into is it its of on
or our the their this to with you your yours via off over under only own all any
linkedin profile page post posts view see get set use using when what which who
""".split())


def tokens(capability: str) -> list[str]:
    """Distinctive words of a capability, for searching the SOURCE."""
    words = re.findall(r"[A-Za-z][A-Za-z0-9]+", capability.lower())
    return [w for w in words if len(w) >= 4 and w not in STOP]


def tool_parameters() -> dict[str, str]:
    """Every parameter of every registered tool -> the tool that declares it.

    **THIS IS THE SIGNAL THAT ACTUALLY CARRIES, AND FINDING THAT OUT COST TWO
    FAILED CONTROLS.** The five filter rows were served by PARAMETERS --
    ``easy_apply``, ``under_ten_applicants``, ``in_your_network``,
    ``fair_chance_employer``, ``job_type`` -- all on one tool. A tool-NAME
    match found `linkedin_apply_job` for "Filter: Easy Apply only", which is
    the wrong tool and would have passed the positive control for the wrong
    reason. A control that can pass on a false match is not yet a control.
    """
    text = SERVER.read_text(encoding="utf-8", errors="replace")
    out: dict[str, str] = {}
    for m in re.finditer(r"async def (linkedin_[a-z0-9_]+)\(([^)]*)\)", text):
        tool, params = m.group(1), m.group(2)
        for pm in re.finditer(r"([a-z][a-z0-9_]{3,})\s*:", params):
            out.setdefault(pm.group(1), tool)
    return out


PARAMS = tool_parameters()


def _stems(words):
    return {w[:-1] if w.endswith("s") and len(w) > 4 else w for w in words}


def source_signals(capability: str) -> tuple[list[str], list[str]]:
    """Evidence in the SOURCE that this capability is already served.

    READS THE CODE, NOT THE CENSUS CELL, and that redesign was forced by a
    control. The first version scanned cell text for words like SHIPPED. Its
    known-answer control found **0 of 7** rows already verified unbanked by
    hand -- because before they were banked those cells read
    ``| 9 | Filter: Easy Apply only | a507441 | GAP | -- |``.

    **THE CELL SAYS NOTHING. THE CENSUS NOT KNOWING THE WORK HAPPENED IS THE
    DEFECT ITSELF**, so a census-text scan can only find rows where somebody
    wrote the evidence in and forgot the state column.

    PROPOSES ONLY. Every hit is printed beside its signal so a reader judges
    it rather than trusts it.
    """
    toks = tokens(capability)
    if not toks:
        return [], []
    stems = _stems(toks)
    sig, hits = [], []

    best, best_n = None, 0
    for param, tool in PARAMS.items():
        shared = stems & _stems(param.split("_"))
        n = len([w for w in shared if len(w) >= 4])
        if n > best_n:
            best, best_n = (param, tool), n
    if best_n >= 1:
        sig.append("PARAM-EXISTS")
        hits.append(f"{best[0]} on {best[1]}")

    for tool in sorted(TOOLS):
        name_stems = _stems(tool[len("linkedin_"):].split("_"))
        shared = {w for w in (stems & name_stems) if len(w) >= 5}
        if shared:
            sig.append("TOOL-NAME-MATCH")
            hits.append(f"{tool} on {'+'.join(sorted(shared))}")
            break

    return sig, hits


def signals(cell: str) -> list[str]:
    """Cell-text signals. KEPT, but demoted -- see source_signals.

    `CONTRADICTS` is the one that still earns its place: a cell announcing its
    own retirement while sitting in GAP disagrees with itself on one line.
    """
    out = []
    if CONTRADICTS.search(cell):
        out.append("CONTRADICTS")
    if SAYS_SHIPPED.search(cell):
        out.append("SAYS-SHIPPED")
    return out


def sweep(ref: str | None = None):
    """Yield (row_id, signals, matches) for every GAP row with a signal."""
    for letter, rid, state, _ln, capability in egr.rows(ref):
        if state != "GAP":
            continue
        sig, hits = source_signals(capability)
        cellsig = signals(_full_cell(letter, rid, ref))
        allsig = cellsig + sig
        if allsig:
            yield f"{letter} {rid}", allsig, hits


_CELL_CACHE: dict[str | None, dict[str, str]] = {}


def _full_cell(letter: str, rid: str, ref: str | None) -> str:
    """The whole row's text. Uses the shipped filter, condition for condition.

    NOT ``egr.rows()``'s fifth element -- that is ``first_prose_cell``, the
    CAPABILITY column, and every signal this file looks for lives in the NOTE
    column. A reader pointed at the wrong column reports a tidy absence; that
    has already happened once in this repository this week.
    """
    if ref not in _CELL_CACHE:
        ccs = egr.ccs
        table: dict[str, str] = {}
        for L, name in ccs.SLICES.items():
            for line in egr.slice_text(name, ref).splitlines():
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
                if not st and L == "N" and egr.ADMIN_ONLY.fullmatch(c[0]):
                    st = "GAP"
                if not st:
                    continue
                table[f"{L} {c[0]}"] = " | ".join(c)
        _CELL_CACHE[ref] = table
    return _CELL_CACHE[ref].get(f"{letter} {rid}", "")


def run_controls() -> bool:
    print("=" * 74)
    print("CONTROLS -- a known-answer test from rows already verified by hand")
    print("=" * 74)
    ok = True
    try:
        flagged = {rid for rid, _s, _t in sweep(CONTROL_REF)}
    except Exception as error:  # noqa: BLE001
        print(f"  POSITIVE control could not run at {CONTROL_REF}: "
              f"{type(error).__name__}: {error}")
        return False

    missed = [r for r in CONTROL_MUST_FLAG if r not in flagged]
    print(f"  1. POSITIVE at {CONTROL_REF}: must flag "
          f"{len(CONTROL_MUST_FLAG)} known-unbanked rows -- "
          f"found {len(CONTROL_MUST_FLAG) - len(missed)}  "
          f"{'PASS' if not missed else 'FAIL'}")
    if missed:
        print(f"       missed: {', '.join(missed)}")
        ok = False

    wrong = [r for r in CONTROL_MUST_NOT_FLAG if r in flagged]
    print(f"  2. NEGATIVE: honestly-GAP rows must NOT flag -- "
          f"{len(wrong)} wrongly flagged  {'PASS' if not wrong else 'FAIL'}")
    if wrong:
        print(f"       wrongly flagged: {', '.join(wrong)}")
        ok = False

    # THE MATCH-QUALITY CONTROL. Runs on TODAY's capability text, which is
    # unchanged for these rows, and asks whether the hit names the thing that
    # actually serves the row.
    caps = {"J 9": "Filter: Easy Apply only",
            "J 11": "Filter: Employment type / job type",
            "J 12": "Filter: Under 10 applicants",
            "J 13": "Filter: In your network",
            "J 14": "Filter: Fair chance employer"}
    bad = []
    for rid, want in CONTROL_EXPECTED_MATCH.items():
        _sig, hits = source_signals(caps[rid])
        if not any(h.split(" on ")[0] == want for h in hits):
            bad.append(f"{rid}: wanted {want}, got {hits or 'nothing'}")
    print(f"  2b. MATCH QUALITY: the hit must name what actually serves the "
          f"row -- {len(bad)} wrong  {'PASS' if not bad else 'FAIL'}")
    for line in bad:
        print(f"       {line}")
    if bad:
        ok = False

    absent_ok = not signals(f"a cell mentioning {ABSENT_SIGNAL} and nothing else")
    print(f"  3. MUST-BE-ABSENT signal raises nothing  "
          f"{'PASS' if absent_ok else 'FAIL'}")
    if not absent_ok:
        ok = False

    print(f"  4. tools read off the server source: {len(TOOLS)}  "
          f"{'PASS' if len(TOOLS) > 20 else 'FAIL -- registry not read'}")
    if len(TOOLS) <= 20:
        ok = False

    print(f"\n  USABLE: {ok}")
    return ok


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not run_controls():
        print("\nCONTROLS FAILED. No candidates printed; a sweep that cannot "
              "find the rows we KNOW were unbanked will not find the rest.")
        return 1
    if "--control" in argv:
        return 0

    rows = sorted(sweep(None), key=lambda r: (-len(r[1]), r[0]))
    order = ["CONTRADICTS", "SAYS-SHIPPED", "PARAM-EXISTS",
             "TOOL-NAME-MATCH"]
    rows.sort(key=lambda r: (order.index(r[1][0]), r[0]))

    if "--tsv" in argv:
        print("row\tsignals\ttools")
        for rid, sig, tools in rows:
            print(f"{rid}\t{','.join(sig)}\t{','.join(tools)}")
        return 0

    print("\n" + "=" * 74)
    print("CANDIDATES -- GAP rows carrying a signal. VERIFY EACH; MOVE NONE")
    print("           -- on this file's say-so alone.")
    print("=" * 74)
    tally = collections.Counter()
    last = None
    for rid, sig, tools in rows:
        tally[sig[0]] += 1
        if sig[0] != last:
            print(f"\n  --- strongest signal: {sig[0]} ---")
            last = sig[0]
        extra = f"  tools={','.join(tools)}" if tools else ""
        print(f"    {rid:8s} {','.join(sig)}{extra}")

    print("\n" + "=" * 74)
    print(f"  {len(rows)} candidates of {sum(1 for _ in egr.rows(None))} "
          f"stated rows")
    for key in order:
        if tally[key]:
            print(f"    {key:14s} {tally[key]:4d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
