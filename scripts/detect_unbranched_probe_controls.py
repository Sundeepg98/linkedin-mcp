"""Find probe self-checks that are computed, printed, and never branched on.

WHY THIS EXISTS. A "control" in ``scripts/_probe_*.py`` is a self-check the
probe runs on itself: a MUST-FIRE needle (present by construction -- a zero
means the instrument is broken) or a MUST-STAY-SILENT needle (absent by
construction -- a non-zero means the matcher is matching itself). The defect
this module finds: the control's result is COMPUTED, then PRINTED (often
with the literal word PASS/FAIL or a note like "must fire"), and then NEVER
BRANCHED ON. No ``if``, no ``return``, no ``raise``, no ``sys.exit``. The
probe prints FAIL and certifies its findings anyway.

Measured 2026-09-20 across the 88 files then in ``scripts/_probe_*.py``: 56
files carry at least one such control (129 instances total, against 762
control-like instances overall -- 630 correctly branch, 129 do not, 13 more
are assigned and never even read). Full census:
``_audit/2026-09-20-control-census.md``. The concrete case that named the
defect and motivated this guard: ``scripts/_probe_events_surface_shape.py``,
fixed in commit ``2fba253`` -- see ``_audit/INSTRUMENTS.md`` entry 24.

METHOD, AST-based (not regex -- a regex over source mis-handles f-strings,
nested calls and multi-line prints). Per function (a nested ``def`` such as
a local ``emit()`` wrapper is its OWN scope, walked separately, so it cannot
pollute its parent's variable set):

1. CANDIDATES: every simple-Name assignment target (``Assign``,
   ``AugAssign``, ``AnnAssign``, ``NamedExpr``, a for-loop target) local to a
   function's own body.
2. SINKS: ``print``, plus any locally-defined function whose own body calls
   ``print`` at least once (catches a thin wrapper such as
   ``def emit(text): print(text); lines.append(text)``).
3. PRINT-ONLY: for every Load of a candidate name, climb its AST ancestors.
   Reaching a ``Call`` to a sink before any statement boundary makes that
   load print-only (this correctly follows the value through ``.format()``,
   ``%``-formatting, ternaries, comparisons and plain-function reformatting,
   none of which are statement boundaries). Reaching a statement boundary
   first (an ``if``/``while`` test, ``assert``, ``return``, a bare compare,
   reassignment elsewhere, ...) makes it a REAL use.
4. CONTROL-LIKE gate: a case-insensitive substring marker (PASS, FAIL,
   CONTROL, "must fire", "must stay silent", "must be", VOID, sanity,
   expected, AGREE, DISAGREE) must appear in the variable's own name OR in a
   NARROW window -- the assignment plus, climbing outward through enclosing
   blocks only as far as needed, the first later sibling statement whose
   subtree contains a sink call referencing the name. The window is
   deliberately narrow (never "the whole function") so a marker word sitting
   in unrelated code elsewhere cannot manufacture a false positive, and it is
   exactly wide enough to catch the case where the marker sits in a sibling
   ``if`` that branches on a DIFFERENT variable, not on the one being
   examined (see the ``hits``/``needle`` example in the module test file).

FINDING = control-like AND every load of the name is print-only (>=1 load
required -- a control-like name with zero loads anywhere is a different,
milder defect, "assigned and never even read", tracked separately).

KNOWN FALSE-POSITIVE MECHANISM, disclosed rather than hidden (a guard whose
failure mode is written down is trustworthy; one that hides it gets
discovered later and discredits everything it passed). The marker list uses
bare short words ("pass", "void") as case-insensitive SUBSTRINGS, exactly as
specified when this was built, and a substring can embed inside an unrelated
identifier: ``scripts/_probe_messaging_menu_enumeration.py``, function
``_report_overlaps``, variables ``one`` and ``overlap_label`` -- the only
marker hit for both is "pass", and the only place "pass" appears in their
window is inside the parameter name ``passes: dict``, not any PASS/FAIL
text. A corpus-wide sweep for this specific mechanism (2026-09-20) found it
responsible for exactly 2 of the then-129 findings (1.6%), both at this one
site, and no other file's classification depends on it. A stricter
word-boundary marker regex was tried as a cross-check and rejected: it also
rejects legitimate inflections with a trailing letter (e.g. "controls", the
plural), which produced a much larger and untrustworthy drop. Anyone
re-tightening the marker rule should re-run that comparison rather than
assume a boundary regex is free.

A SECOND FALSE-POSITIVE MECHANISM, MEASURED 2026-09-20 AND LARGER THAN THE
FIRST. The marker "pass" also matches the bare Python ``pass`` STATEMENT, which
is the idiomatic body of a swallowed ``except`` and therefore sits inside the
window of any value read in a ``try``. The value is then the probe's INPUT and
not a control at all::

    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception:
        pass                      # <- the only marker in the window
    print(f"... {len(main_text.split(needle)) - 1}")

A corpus-wide sweep (strip every line that is a bare ``pass`` statement from
each finding's window, re-test for a marker, and count the findings that lose
their last one) returned **4 of the 133 live findings, 3.0%**: two in
``_probe_small_measures_followup.py`` ``part_b_suggested_filters`` (``html``,
``main_text``) and two in ``_probe_small_measures_live.py`` (``_needles`` and
``read_feed_hashtag_context``, both ``main_text``). All four are named with
their reasons in the baseline. THE DETECTOR IS NOT CHANGED HERE: narrowing the
marker rule would move a published 129-row census, which is a wave of its own
and not a footnote -- and the boundary-regex alternative was already tried and
rejected for over-rejecting legitimate inflections (above).

A THIRD MECHANISM, same sweep: the window is *"as far as the first later
sibling statement whose subtree contains a sink call referencing the name"*,
which for a REPORT ACCUMULATOR written by a nested ``emit()`` and flushed by a
``_write(lines)`` that prints, stretches across whatever the probe happened to
announce in between. ``_probe_job_search_result_sets.py`` ``main() -> lines``
is flagged solely because an ``emit("positive control keyword: ...")`` string
sits ten lines into a 28-line window. Also unchanged, for the same reason.

ALSO DISCLOSED: for-loop/async-for targets are included as candidates (25.6%
of the 129 at last count) and are structurally weaker evidence than a
computed Assign/AugAssign/NamedExpr value -- a loop target is sometimes a
display label riding beside a properly-branched verdict computed elsewhere
in the same iteration (see ``assign_kind`` in the JSON/baseline output).

Usage::

    ./venv/Scripts/python.exe scripts/detect_unbranched_probe_controls.py
    ./venv/Scripts/python.exe scripts/detect_unbranched_probe_controls.py --json out.json
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

MARKERS = [
    "pass",
    "fail",
    "control",
    "must fire",
    "must stay silent",
    "must be",
    "void",
    "sanity",
    "expected",
    "agree",
    "disagree",
]


def has_marker(text: str) -> tuple[bool, list[str]]:
    low = text.lower()
    hit = [m for m in MARKERS if m in low]
    return (len(hit) > 0, hit)


def build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def scope_nodes(func: ast.FunctionDef | ast.AsyncFunctionDef):
    """Yield every descendant of func's body WITHOUT descending into a
    nested def/lambda's own body (that interior belongs to its own scope
    walk when ast.walk reaches it separately)."""

    def walk(node: ast.AST):
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return
        for child in ast.iter_child_nodes(node):
            yield from walk(child)

    for stmt in func.body:
        yield from walk(stmt)


def find_sinks(tree: ast.AST) -> set[str]:
    """``print`` plus any locally-defined function whose own body calls
    ``print`` at least once."""
    sinks = {"print"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in scope_nodes(node):
                if (isinstance(sub, ast.Call)
                        and isinstance(sub.func, ast.Name)
                        and sub.func.id == "print"):
                    sinks.add(node.name)
                    break
    return sinks


def is_sink_nested(name_node: ast.Name, parents: dict, sinks: set[str]) -> bool:
    node: ast.AST = name_node
    while node in parents:
        parent = parents[node]
        if (isinstance(parent, ast.Call)
                and isinstance(parent.func, ast.Name)
                and parent.func.id in sinks):
            return True
        if isinstance(parent, ast.stmt):
            return False
        node = parent
    return False


def enclosing_stmt(node: ast.AST, parents: dict) -> ast.stmt | None:
    cur = node
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, ast.stmt):
            return cur
    return None


def assign_targets(stmt: ast.stmt) -> list[tuple[str, ast.stmt]]:
    names: list[str] = []

    def collect(target: ast.AST):
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                collect(elt)
        elif isinstance(target, ast.Starred):
            collect(target.value)

    if isinstance(stmt, ast.Assign):
        for t in stmt.targets:
            collect(t)
    elif isinstance(stmt, ast.AugAssign):
        collect(stmt.target)
    elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
        collect(stmt.target)
    elif isinstance(stmt, (ast.For, ast.AsyncFor)):
        collect(stmt.target)
    return [(n, stmt) for n in names]


def find_window(
    assign_stmt: ast.stmt,
    name: str,
    parents: dict,
    sinks: set[str],
    source_lines: list[str],
) -> str:
    """Climb from assign_stmt's own body-list upward; at each level scan
    forward from the assignment's position for the first sibling statement
    whose subtree contains a sink call referencing ``name``. Return the
    source text of [assignment .. that sibling] (inclusive)."""
    child = assign_stmt
    cur_parent = parents.get(assign_stmt)
    while cur_parent is not None:
        body_list = None
        for field in ("body", "orelse", "finalbody"):
            lst = getattr(cur_parent, field, None)
            if isinstance(lst, list) and child in lst:
                body_list = lst
                break
        if body_list is not None:
            start_idx = body_list.index(child)
            for j in range(start_idx, len(body_list)):
                candidate = body_list[j]
                found = False
                for sub in ast.walk(candidate):
                    if (isinstance(sub, ast.Call)
                            and isinstance(sub.func, ast.Name)
                            and sub.func.id in sinks):
                        for inner in ast.walk(sub):
                            if (isinstance(inner, ast.Name)
                                    and inner.id == name
                                    and isinstance(inner.ctx, ast.Load)):
                                found = True
                                break
                    if found:
                        break
                if found:
                    start_line = body_list[start_idx].lineno
                    end_line = getattr(candidate, "end_lineno", candidate.lineno)
                    return "\n".join(source_lines[start_line - 1:end_line])
        child = cur_parent
        cur_parent = parents.get(cur_parent)
    start_line = assign_stmt.lineno
    end_line = getattr(assign_stmt, "end_lineno", start_line)
    return "\n".join(source_lines[start_line - 1:end_line])


def analyse_source(source: str, filename: str = "<string>") -> dict:
    """Analyse Python SOURCE TEXT directly (no filesystem access) -- the
    entry point the test fixtures use, so the discrimination proof needs no
    file on disk at all."""
    raw_has_marker, _ = has_marker(source)
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return {"file": filename, "parse_ok": False, "error": f"SyntaxError: {exc}",
                "raw_has_marker": raw_has_marker}

    source_lines = source.splitlines()
    parents = build_parent_map(tree)
    sinks = find_sinks(tree)

    findings = []
    branched_controls = []
    unused_controls = []

    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        first_assign: dict[str, ast.stmt] = {}
        for node in scope_nodes(func):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                  ast.For, ast.AsyncFor)):
                for name, stmt in assign_targets(node):
                    first_assign.setdefault(name, stmt)
            if isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name):
                first_assign.setdefault(node.target.id, enclosing_stmt(node, parents) or func)

        loads: dict[str, list[ast.Name]] = {}
        for node in scope_nodes(func):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                loads.setdefault(node.id, []).append(node)

        for name, assign_stmt in first_assign.items():
            name_marker, name_hits = has_marker(name)
            window_text = find_window(assign_stmt, name, parents, sinks, source_lines)
            window_marker, window_hits = has_marker(window_text)
            if not (name_marker or window_marker):
                continue

            name_loads = loads.get(name, [])
            assign_line = assign_stmt.lineno
            assign_src = (source_lines[assign_line - 1].strip()
                          if assign_line - 1 < len(source_lines) else "")
            assign_kind = ("for_target" if isinstance(assign_stmt, (ast.For, ast.AsyncFor))
                           else "assign")

            if not name_loads:
                unused_controls.append({
                    "function": func.name, "variable": name, "line": assign_line,
                    "assign_src": assign_src,
                })
                continue

            sink_flags = [is_sink_nested(ld, parents, sinks) for ld in name_loads]
            entry = {
                "function": func.name,
                "variable": name,
                "line": assign_line,
                "assign_src": assign_src,
                "assign_kind": assign_kind,
                "markers": sorted(set(name_hits + window_hits)),
                "num_loads": len(name_loads),
                "num_non_sink_loads": sink_flags.count(False),
            }
            if all(sink_flags):
                findings.append(entry)
            else:
                branched_controls.append(entry)

    return {
        "file": filename,
        "parse_ok": True,
        "raw_has_marker": raw_has_marker,
        "findings": findings,
        "branched_controls": branched_controls,
        "unused_controls": unused_controls,
    }


def analyse_file(path: Path) -> dict:
    try:
        source = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        return {"file": path.name, "parse_ok": False, "error": f"READ ERROR: {exc}"}
    result = analyse_source(source, filename=path.name)
    return result


def scan_corpus(glob_pattern: str = "scripts/_probe_*.py") -> list[dict]:
    files = sorted(REPO.glob(glob_pattern))
    return [analyse_file(p) for p in files]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=None,
                         help="write full machine-readable results here")
    parser.add_argument("--glob", default="scripts/_probe_*.py",
                         help="corpus glob, relative to the repo root")
    args = parser.parse_args()

    results = scan_corpus(args.glob)
    n_files = len(results)
    n_parse_fail = sum(1 for r in results if not r.get("parse_ok"))
    files_with_finding = [r for r in results if r.get("findings")]
    total_findings = sum(len(r.get("findings", [])) for r in results)
    total_branched = sum(len(r.get("branched_controls", [])) for r in results)

    print(f"corpus: {n_files} files ({args.glob})")
    print(f"parse failures: {n_parse_fail}")
    print(f"files with >=1 never-branched control: {len(files_with_finding)}")
    print(f"never-branched instances: {total_findings}")
    print(f"correctly-branched control-like instances: {total_branched}")

    if args.json:
        args.json.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
        print(f"wrote {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
