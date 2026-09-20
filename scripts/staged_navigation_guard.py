"""The navigation and tainted-output sweeps, asked about the change, not the tree.

WHAT THIS IS THE OTHER HALF OF.

``tests/test_navigation_is_never_derived.py`` runs two rules over every python
file in ``scripts/`` and ``linkedin_server/``:

    test_no_navigation_is_aimed_at_a_url_the_browser_chose
        every ``goto`` argument is a value this repository authored
    test_no_navigation_derived_value_reaches_an_output_sink
        no value the browser chose reaches a print or a log

Each is parametrised over the 170 scanned files, and the per-case cost does not
collapse after the first -- every case re-pays a real per-file AST scan.
Measured 2026-09-20 on this box: 342 of the file's 373 cases are those two
families, and the file is 8.4s. After this wave's other two repairs it is **the
single most expensive member of ``scripts/impact_gate.py``'s unconditional
floor**, which makes it the thing that sets the floor's wall clock: the gate
runs the floor under ``--dist loadfile``, which pins a file to one worker, so
the floor can never be faster than its slowest single file.

BOTH RULES ARE PER-FILE AND THAT IS WHY THIS IS POSSIBLE.

    violations(text, name)        == KNOWN_DERIVED_NAVIGATIONS.get(name, [])
    output_violations(text, name) == KNOWN_TAINTED_OUTPUT.get(name, [])

The verdict on a file is a function of that file's own text and its own row in
a declaration table. No other file's content enters it. So checking only the
files this commit writes gives the same answer for those files -- and for the
files it does not write, the answer has not changed since the last time the
whole set was checked.

**THAT LAST CLAUSE IS A BASE CASE AND IT IS NOT OPTIONAL.** This is an
INDUCTION STEP. Its base case is the whole-tree form, which is not deleted and
does not move: it stays in ``tests/`` and runs on every push, on three
platforms, in ``.github/workflows/ci.yml``.

    base case        the whole-tree sweep, in CI, on every push
    induction step   this script, locally, on every commit

THE EQUALITY IS TWO-SIDED AND THE SIBLING KEEPS IT THAT WAY. The whole-tree
form asserts the found set EQUALS the declared set, so it fails when a site is
ADDED and equally when a site is FIXED and its declaration left behind. A
one-sided ``<=`` here would quietly permit the second, which is the half that
stops a "known hole" note outliving the hole -- this repository has a standing
receipt for exactly that, a declared site that was dead for ten days.

WHEN IT REFUSES TO BE THE FAST PATH (exit 2).

  * the property module cannot be imported;
  * **the property module is itself in the change set.** The two declaration
    tables and both detectors live in it, so a commit that edits it has
    changed what the question MEANS for the files this run does not read. That
    is the set-shaped residue of an otherwise per-file property, computed from
    the diff rather than assumed away;
  * git could not say what changed -- an unknown change set is not an empty one.

THE SCANNED SET IS A ONE-LEVEL GLOB, NOT A WALK. The whole-tree form uses
``(REPO / folder).glob("*.py")`` for exactly two folders, so a staged path only
qualifies when it sits DIRECTLY in ``scripts/`` or ``linkedin_server/``. A
nested file is not scanned there and must not be scanned here; checking more
than the twin would produce refusals the whole-tree form does not, and a fast
half that disagrees with its slow half in either direction is not a pair.

THE DECLARATION TABLES ARE KEYED BY BASENAME, and this script keys them the
same way rather than by repo-relative path. Same table, same key, one rule.

EXIT CODES:

    0   examined N files, both rules agree with the declarations
    1   REFUSED: a file this commit would write disagrees
    2   CANNOT ANSWER -- run the whole-tree form instead. NOT an all-clear.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent.parent

PROPERTY_MODULE = SCRIPT_ROOT / "tests" / "test_navigation_is_never_derived.py"

#: Staging this changes both detectors and both declaration tables at once.
PROPERTY_PATHS = ("tests/test_navigation_is_never_derived.py",)

#: The twin's own scanned folders, as a one-level glob. Kept as a constant here
#: and CHECKED against the module's ``SCANNED`` at run time, so the two cannot
#: drift apart silently.
FOLDERS = ("scripts", "linkedin_server")

CLEAN, REFUSED, CANNOT_ANSWER = 0, 1, 2


def _git(repo: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], cwd=str(repo),
        capture_output=True, text=True, errors="replace",
    )
    return proc.returncode, proc.stdout


def _load_property():
    if str(SCRIPT_ROOT) not in sys.path:
        sys.path.insert(0, str(SCRIPT_ROOT))
    spec = importlib.util.spec_from_file_location(
        "_navigation_property", PROPERTY_MODULE)
    if spec is None or spec.loader is None:
        raise ImportError("could not build a spec for " + str(PROPERTY_MODULE))
    module = importlib.util.module_from_spec(spec)
    sys.modules["_navigation_property"] = module
    spec.loader.exec_module(module)
    return module


def in_scope(rel: str) -> bool:
    """Directly inside one of the scanned folders, and a ``.py``.

    ``scripts/foo.py`` yes; ``scripts/sub/foo.py`` no, because the twin's glob
    does not recurse and a fast half that checks MORE than its slow half is as
    broken as one that checks less.
    """
    parts = rel.split("/")
    return (len(parts) == 2 and parts[0] in FOLDERS
            and parts[1].endswith(".py"))


def change_set(repo: Path, explicit: list[str] | None) -> list[tuple[str, str]] | None:
    """``(path, source)`` for everything this commit would write, in scope."""
    if explicit is not None:
        pairs = [(rel, "index") for rel in explicit]
    else:
        code, out = _git(repo, "diff", "--cached", "--name-only",
                         "--diff-filter=ACMR")
        if code != 0:
            return None
        staged = [line for line in out.splitlines() if line.strip()]
        code, out = _git(repo, "ls-files", "--others", "--exclude-standard")
        if code != 0:
            return None
        untracked = [line for line in out.splitlines() if line.strip()]
        seen = set(staged)
        pairs = ([(rel, "index") for rel in staged]
                 + [(rel, "worktree") for rel in untracked if rel not in seen])
    return [(rel, source) for rel, source in pairs if in_scope(rel)]


def read(repo: Path, rel: str, source: str) -> str | None:
    if source == "index":
        code, out = _git(repo, "show", ":" + rel)
        return None if code != 0 else out
    try:
        return (repo / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=None)
    parser.add_argument("--paths", nargs="*", default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve() if args.repo else SCRIPT_ROOT

    try:
        prop = _load_property()
    except Exception as exc:  # noqa: BLE001
        print(f"staged-navigation: the property module would not import "
              f"({type(exc).__name__}: {exc}). CANNOT ANSWER -- run "
              f"tests/test_navigation_is_never_derived.py.", file=sys.stderr)
        return CANNOT_ANSWER

    if tuple(getattr(prop, "SCANNED", ())) != FOLDERS:
        # THE TWIN WIDENED OR NARROWED ITS SCOPE AND THIS DID NOT. Declining is
        # the only honest answer: a fast half aimed at a different set of files
        # from its slow half is not a pair, whichever way the difference runs.
        print(f"staged-navigation: the twin now scans "
              f"{getattr(prop, 'SCANNED', None)!r} and this script is written "
              f"for {FOLDERS!r}. CANNOT ANSWER -- run the whole-tree form and "
              "update this script's FOLDERS in the same commit.",
              file=sys.stderr)
        return CANNOT_ANSWER

    changed = change_set(repo, args.paths)
    if changed is None:
        print("staged-navigation: git could not say what changed, so the "
              "change set is UNKNOWN -- not empty. CANNOT ANSWER.",
              file=sys.stderr)
        return CANNOT_ANSWER

    code, out = _git(repo, "diff", "--cached", "--name-only",
                     "--diff-filter=ACMR")
    staged_all = [line for line in out.splitlines() if line.strip()] if code == 0 else []
    touched = sorted(set(staged_all) & set(PROPERTY_PATHS))
    if touched:
        print("staged-navigation: this change edits the property itself (" +
              ", ".join(touched) + "), so both detectors and both declaration "
              "tables may have moved. A staged-set answer is no longer "
              "evidence about the files it did not read. CANNOT ANSWER -- run "
              "tests/test_navigation_is_never_derived.py.", file=sys.stderr)
        return CANNOT_ANSWER

    problems: list[str] = []
    examined = 0
    for rel, source in changed:
        text = read(repo, rel, source)
        if text is None:
            continue
        name = rel.rsplit("/", 1)[-1]
        examined += 1
        try:
            found_nav = [expr for _line, expr in prop.violations(text, name)]
            found_out = [what for _line, what in prop.output_violations(text, name)]
        except SyntaxError:
            # A FILE MID-EDIT IS NOT EVIDENCE ABOUT THIS RULE, and the twin
            # takes the same view elsewhere. It is also not an all-clear, so
            # say it rather than skipping quietly.
            print(f"staged-navigation: {rel} does not parse; it was NOT "
                  "checked. The whole-tree form will see it.", file=sys.stderr)
            continue
        declared_nav = prop.KNOWN_DERIVED_NAVIGATIONS.get(name, [])
        declared_out = prop.KNOWN_TAINTED_OUTPUT.get(name, [])
        if found_nav != declared_nav:
            problems.append(
                f"  {rel}: derived-navigation sites are {found_nav} and the "
                f"declared set is {declared_nav}")
        if found_out != declared_out:
            problems.append(
                f"  {rel}: tainted-output sites are {found_out} and the "
                f"declared set is {declared_out}")

    if problems:
        print("", file=sys.stderr)
        print("REFUSED: a file this commit would write disagrees with its "
              "navigation declaration.", file=sys.stderr)
        print("", file=sys.stderr)
        for line in problems:
            print(line, file=sys.stderr)
        print("", file=sys.stderr)
        print("THE COMPARISON IS AN EQUALITY, SO THIS FIRES BOTH WAYS. If you "
              "ADDED a site, navigate a module-level constant or emit a "
              "RELATION instead. If you FIXED one, delete its entry from "
              "KNOWN_DERIVED_NAVIGATIONS / KNOWN_TAINTED_OUTPUT in "
              "tests/test_navigation_is_never_derived.py -- a declaration "
              "outliving its hole is a comment pretending to be a check.",
              file=sys.stderr)
        return REFUSED

    if not args.quiet:
        if examined == 0:
            print("staged-navigation: examined 0 files. Nothing this commit "
                  "writes sits directly in " + "/ or ".join(FOLDERS) +
                  "/, so this is a statement about the CHANGE SET and not "
                  "about the tree.", file=sys.stderr)
        else:
            print(f"staged-navigation: {examined} file(s) examined, both "
                  "rules agree with their declarations. The other scanned "
                  "files were NOT read; their base case is the whole-tree "
                  "sweep in CI.", file=sys.stderr)
    return CLEAN


if __name__ == "__main__":
    raise SystemExit(main())
