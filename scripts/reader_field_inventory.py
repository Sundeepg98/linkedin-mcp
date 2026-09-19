"""Every FIELD every reader emits, and whether a caller can actually receive it.

**THE FINDING THIS IS BUILT FROM.** One dict in ``dom.read_job_insight_panels``
carries SEVEN fields and each serves a different census row. Six were banked on
2026-09-19 through one seam (built-after-the-freeze) and the seventh, ``J 27``,
had been banked hours earlier through a completely different one (a COVERED
twin in another slice). **The same code was reachable by two seams and neither
found all of it.**

Nothing in this repository lists what a reader EMITS. The census lists
capabilities, the tool surface lists parameters, the unwired-reader guard lists
function names. **A field is the unit that maps to a census row, and it was the
one unit nobody had enumerated.**

=============================================================================
WHY THIS IS NOT THE FAILED SWEEP WEARING A NEW HAT
=============================================================================

``scripts/unbanked_row_sweep.py`` is committed as a FAILED instrument that
refuses to run: four designs, four failures, because matching a capability
SENTENCE to the code that serves it is semantic and no token overlap expresses
it.

**THIS FILE DOES NOT MATCH ANYTHING.** It reads the AST and reports what the
code contains. It emits no verdict about any census row and cannot be wrong
about one, because it never mentions one. What it produces is a WORKLIST a
person reads -- which is the only method that has ever produced a correct
answer here.

    unbanked_row_sweep   capability sentence -> code        SEMANTIC, failed
    this file            code -> fields it emits            SYNTACTIC, sound

=============================================================================
THE TWO QUESTIONS IT ANSWERS, AND THE SECOND IS THE ONE THAT MATTERS
=============================================================================

**1. WHAT DOES THIS READER EMIT?** String keys of dict literals it returns.

**2. CAN A CALLER RECEIVE IT?** A field in a reader nobody calls is not
coverage. This walks the call graph from every ``linkedin_*`` tool, so a
reader reachable from a tool is marked REACHED and one that is not is marked
ORPHAN. **That distinction is exactly the one that banked six rows**: *"the
reader emits it" and "a caller receives it" are different claims, and only the
second banks a row.*

**WHAT IT CANNOT SEE, stated rather than discovered later:** a field added to
a dict by ``update()`` or a comprehension rather than written as a literal key;
a reader reached only through a dynamic dispatch; and whether a REACHED field
survives the shaper on the way out. It reports syntax, and the caller check is
one hop's worth of honesty rather than a proof.

Run::

    ./venv/Scripts/python.exe scripts/reader_field_inventory.py --control
    ./venv/Scripts/python.exe scripts/reader_field_inventory.py
    ./venv/Scripts/python.exe scripts/reader_field_inventory.py --tsv
"""
from __future__ import annotations

import ast
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PKG = ROOT / "linkedin_server"

#: KNOWN ANSWERS, every one verified by hand against the tree on 2026-09-19 and
#: banked in the census. A sweep that cannot find the fields we KNOW are there
#: will not find the ones we do not.
CONTROL_MUST_FIND: dict[str, tuple[str, ...]] = {
    "read_job_insight_panels": (
        "applicant_insights", "company_insights", "promoted",
        "responses_managed_off_linkedin", "verified_job",
    ),
    "read_profile_views_insights": ("trend",),
    # THESE TWO ARE HERE BECAUSE A MUTATION SURVIVED, AND THE FIX WAS THE
    # INPUT RATHER THAN THE ASSERTION.
    #
    # Deleting ``_assigned_dict_keys`` -- the ``out = {...}; return out``
    # walk -- left the control GREEN, because both readers above are ALSO
    # findable by the return-literal walk. The branch looked untested and was
    # in fact doing most of the work: measured, **27 readers are found by the
    # assigned-dict walk ALONE**, against 11 by return-literal alone and 5 by
    # both.
    #
    # So the first control set was chosen from the author's model of the risk
    # instead of from the BRANCH STRUCTURE of the thing under test -- the
    # failure this repository has now caught four times. These two readers are
    # findable ONLY by that branch, so deleting it now kills the control.
    # Both were verified by hand this session: read_group_memberships banked
    # M C60 and N 173, read_events_home banked N 180.
    "read_group_memberships": ("memberships", "agrees_with_corroborated"),
    "read_events_home": ("registered_events", "verdict"),
}
#: A field name no reader emits. A scanner that finds it is matching itself.
ABSENT_FIELD = "zqxjvbnm_not_a_field"


def _modules() -> dict[str, ast.AST]:
    out: dict[str, ast.AST] = {}
    for path in sorted(PKG.glob("*.py")):
        try:
            out[path.stem] = ast.parse(
                path.read_text(encoding="utf-8", errors="replace")
            )
        except SyntaxError:
            continue
    return out


def _dict_keys(node: ast.AST) -> set[str]:
    """String keys of every dict literal RETURNED inside this function.

    Only ``return``ed dicts, and only literal keys. A key built at runtime is
    not a field this file can name, and pretending otherwise would put a
    guessed string in a worklist a person is about to trust.
    """
    keys: set[str] = set()
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Return) or sub.value is None:
            continue
        for inner in ast.walk(sub.value):
            if isinstance(inner, ast.Dict):
                for key in inner.keys:
                    if isinstance(key, ast.Constant) and isinstance(
                        key.value, str
                    ):
                        keys.add(key.value)
    return keys


def _assigned_dict_keys(node: ast.AST) -> set[str]:
    """Keys of a dict literal ASSIGNED to a local that is later returned.

    ``read_job_insight_panels`` builds ``out = {...}`` and returns ``out``, so
    a return-only walk finds nothing. **That case is the whole reason this
    file exists**, which makes it the one shape it must not miss.
    """
    returned: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Name):
            returned.add(sub.value.id)
    if not returned:
        return set()
    keys: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Assign) and isinstance(sub.value, ast.Dict):
            targets = {t.id for t in sub.targets if isinstance(t, ast.Name)}
            if targets & returned:
                for key in sub.value.keys:
                    if isinstance(key, ast.Constant) and isinstance(
                        key.value, str
                    ):
                        keys.add(key.value)
        # ``out["x"] = ...`` on a returned local is also a field.
        if isinstance(sub, ast.Assign):
            for tgt in sub.targets:
                if (
                    isinstance(tgt, ast.Subscript)
                    and isinstance(tgt.value, ast.Name)
                    and tgt.value.id in returned
                    and isinstance(tgt.slice, ast.Constant)
                    and isinstance(tgt.slice.value, str)
                ):
                    keys.add(tgt.slice.value)
    return keys


def _called_names(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Name):
                out.add(func.id)
            elif isinstance(func, ast.Attribute):
                out.add(func.attr)
    return out


def inventory() -> dict[str, dict]:
    mods = _modules()
    funcs: dict[str, tuple[str, ast.AST]] = {}
    for mod, tree in mods.items():
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.setdefault(node.name, (mod, node))

    tools = [
        name for name in funcs if name.startswith("linkedin_")
    ]
    # Reachability from any tool, transitively.
    reached: set[str] = set()
    frontier = list(tools)
    while frontier:
        current = frontier.pop()
        if current in reached:
            continue
        reached.add(current)
        entry = funcs.get(current)
        if not entry:
            continue
        for callee in _called_names(entry[1]):
            if callee in funcs and callee not in reached:
                frontier.append(callee)

    out: dict[str, dict] = {}
    for name, (mod, node) in sorted(funcs.items()):
        if not name.startswith("read_"):
            continue
        fields = _dict_keys(node) | _assigned_dict_keys(node)
        if not fields:
            continue
        out[name] = {
            "module": mod,
            "fields": sorted(fields),
            "reached": name in reached,
        }
    return out


def run_controls(inv: dict[str, dict]) -> bool:
    print("=" * 74)
    print("CONTROLS -- known answers, every one verified by hand and banked")
    print("=" * 74)
    ok = True
    for reader, must in CONTROL_MUST_FIND.items():
        got = set(inv.get(reader, {}).get("fields") or [])
        missing = [f for f in must if f not in got]
        print(f"  {reader:32s} {len(must) - len(missing)}/{len(must)} found  "
              f"{'PASS' if not missing else 'FAIL'}")
        if missing:
            print(f"      missing: {', '.join(missing)}")
            ok = False
        if not inv.get(reader, {}).get("reached"):
            print(f"      FAIL: {reader} is not REACHED from any tool, but "
                  f"its fields were banked as covered")
            ok = False
    everywhere = {f for v in inv.values() for f in v["fields"]}
    absent_ok = ABSENT_FIELD not in everywhere
    print(f"  {'MUST-BE-ABSENT field':32s} {'PASS' if absent_ok else 'FAIL'}")
    if not absent_ok:
        ok = False
    print(f"  {'readers with fields':32s} {len(inv)}  "
          f"{'PASS' if len(inv) > 5 else 'FAIL -- nothing was parsed'}")
    if len(inv) <= 5:
        ok = False
    print(f"\n  USABLE: {ok}")
    return ok


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    inv = inventory()
    if not run_controls(inv):
        print("\nCONTROLS FAILED. No inventory printed.")
        return 1
    if "--control" in argv:
        return 0

    if "--tsv" in argv:
        print("reader\tmodule\treached\tfields")
        for name, rec in inv.items():
            print(f"{name}\t{rec['module']}\t{rec['reached']}\t"
                  f"{','.join(rec['fields'])}")
        return 0

    reached = {k: v for k, v in inv.items() if v["reached"]}
    orphan = {k: v for k, v in inv.items() if not v["reached"]}
    total = sum(len(v["fields"]) for v in inv.values())
    print("\n" + "=" * 74)
    print("FIELDS A CALLER CAN RECEIVE -- each is a candidate census row")
    print("=" * 74)
    for name, rec in sorted(reached.items(),
                            key=lambda kv: -len(kv[1]["fields"])):
        print(f"\n  {name}  ({rec['module']}.py, {len(rec['fields'])} fields)")
        print("      " + "  ".join(rec["fields"]))

    print("\n" + "=" * 74)
    print("ORPHANS -- emitted by a reader no tool reaches. NOT coverage.")
    print("=" * 74)
    for name, rec in sorted(orphan.items()):
        print(f"  {name:38s} {rec['module']}.py  {len(rec['fields'])} fields")

    print("\n" + "=" * 74)
    print(f"  {len(inv)} readers, {total} fields, "
          f"{len(reached)} reached, {len(orphan)} orphan")
    print("  EVERY REACHED FIELD IS A CANDIDATE, NEVER A FINDING. A person "
          "reads this; it matches no census row and cannot be wrong about "
          "one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
