"""The SHAPE half of the identity guard, asked about the change instead of the tree.

WHAT THIS IS THE OTHER HALF OF.

``tests/test_no_committed_identity.py`` parametrises one assertion over every
committable file -- 545 tracked plus every untracked-not-ignored one -- and
asks each in turn whether it carries an identifier SHAPE that nothing has
declared. It is the most expensive single guard in this repository: measured
2026-09-20 on this box, 17,996 ms alone, against a 719 ms cheapest floor
member and a ~2,900 ms pytest startup. ``scripts/impact_gate.py`` runs it
UNCONDITIONALLY, because a sweep of the tracked set is coupled to everything
and therefore to nothing in particular, so no impact analysis can select it.

This script asks the SAME question of the SAME property about a different set:
the files this commit would actually write.

    whole tree   545 files, every commit, 17,996 ms
    this script  the staged set, typically 1-5 files

**IT IS AN INDUCTION STEP AND IT IS UNSOUND WITHOUT ITS BASE CASE.** "No
committable file carries an undeclared shape" is preserved by checking only
the staged files ONLY IF it already held on the tree those files are landing
on. Nothing local guarantees that: a ``--no-verify`` commit, a guard disarmed
in a worktree, or a merge from a branch that never ran it all break it. The
base case is the WHOLE-TREE FORM, which keeps running -- on every push, on
three platforms, in ``.github/workflows/ci.yml``. Delete that and this script
stops being a fast check and becomes a fast guess.

    base case        the whole-tree sweep in CI, re-established on every push
    induction step   this script, on every commit, locally

Neither is optional and neither replaces the other. A reader who removes the
sweep because this one passes has traded a guarantee for a heuristic.

THE UNTRACKED FILES ARE PART OF THE CHANGE SET, NOT PART OF THE TREE.

``committable_files()`` was widened on 2026-09-01 because a file carrying a
real activity id sat UNTRACKED through a green suite and became visible only
in the commit that published it. That widening has no base case in CI at all:
CI clones a commit, so it never sees an untracked file, and it never will.
**Those files therefore stay in the fast set**, where they cost one read each
rather than being deferred to a sweep that structurally cannot see them.

    staged      content read from the INDEX, which is what the blob will hold
    untracked   content read from the WORKING TREE, because there is no blob yet
    tracked-and-unchanged   not read here. CI is its base case.

WHEN IT REFUSES TO BE THE FAST PATH (exit 2), and why that is not fail-open.

Every other gate in this repository fails OPEN, because refusing work over
broken infrastructure trains everybody to pass ``--no-verify``. This one has
somewhere better to fail TO: the whole-tree form still exists and costs 18
seconds. So it fails to the SLOW PATH and says so, in three cases:

  * the property module cannot be imported -- two instruments that disagree
    about what a shape is are worse than one slow instrument;
  * **the property module is itself in the change set.** ``DECLARED_PLANTS``
    is a per-file allowance table and ``SHAPES`` is the rule set; a commit
    that edits either has changed what the question MEANS, so HEAD's green is
    no longer evidence about the files this run does not read. This is the
    set-shaped residue of an otherwise per-file property, and it is computed
    from the diff rather than assumed away;
  * git could not say what changed -- an unknown change set is not an empty one.

THE ONE THING IT MUST NEVER DO, inherited verbatim from the pre-commit hook:
print the matched value. It reports FILE, LINE, CLASS and a masked span, using
this repository's own ``redact``.

WHY NOT FOLD THIS INTO ``scripts/pre_commit_identity_gate.py``. That hook
deliberately runs the EXACT-VALUE wordlist only, and its docstring gives the
reason: a hook that asks a committer to adjudicate a SHAPE at commit time gets
bypassed within the hour, and a bypassed hook is worse than none. That ruling
stands and this script does not touch it. **The consumer here is the impact
gate, not the hook** -- and the gate already adjudicates these shapes today,
on 545 files instead of on the handful the committer actually wrote. This
reduces what a committer is asked to judge; it does not add to it.

USAGE

    python scripts/staged_identity_shapes.py            # the index
    python scripts/staged_identity_shapes.py --paths a b # explicit paths
    python scripts/staged_identity_shapes.py --repo DIR  # another git tree

EXIT CODES, and the caller must distinguish all three:

    0   examined N files, none carries an undeclared shape
    1   REFUSED: a file this commit would write carries one
    2   CANNOT ANSWER -- run the whole-tree form instead. NOT an all-clear.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent.parent

#: The single definition of the property. IMPORTED, never copied -- two
#: spellings of one rule drift, and the drift is invisible until the day they
#: disagree about a real value. This is the same reason
#: ``pre_commit_identity_gate.py`` imports the sweep rather than restating the
#: wordlist.
PROPERTY_MODULE = SCRIPT_ROOT / "tests" / "test_no_committed_identity.py"

#: Staging THIS changes what the question means, so a staged-set answer stops
#: being evidence about the files it did not read. See the docstring.
PROPERTY_PATHS = (
    "tests/test_no_committed_identity.py",
    "tests/test_no_committed_credential.py",  # owns committable_files()
    "tests/leakwalk.py",                      # owns the spelling expander
)

CLEAN, REFUSED, CANNOT_ANSWER = 0, 1, 2


def _git(repo: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], cwd=str(repo),
        capture_output=True, text=True, errors="replace",
    )
    return proc.returncode, proc.stdout


def _load_property():
    """``(hits_in, redact, DECLARED_PLANTS, HASHY, BINARY_SUFFIXES)``.

    Importing a pytest module from a plain script is deliberate and is what
    keeps there being ONE rule. ``tests`` must be importable as a package for
    its own ``from tests.leakwalk import ...``, so the repo root goes on the
    path first.
    """
    if str(SCRIPT_ROOT) not in sys.path:
        sys.path.insert(0, str(SCRIPT_ROOT))
    spec = importlib.util.spec_from_file_location(
        "_identity_property", PROPERTY_MODULE)
    if spec is None or spec.loader is None:
        raise ImportError("could not build a spec for " + str(PROPERTY_MODULE))
    module = importlib.util.module_from_spec(spec)
    sys.modules["_identity_property"] = module
    spec.loader.exec_module(module)
    return module


def change_set(repo: Path, explicit: list[str] | None) -> list[tuple[str, str]] | None:
    """``(path, source)`` for everything this commit would write.

    ``source`` is ``"index"`` or ``"worktree"`` and decides which bytes get
    read. Returns None when git could not answer, which is an UNKNOWN change
    set and must never be reported as an empty one.
    """
    if explicit is not None:
        return [(rel, "index") for rel in explicit]
    code, out = _git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if code != 0:
        return None
    staged = [line for line in out.splitlines() if line.strip()]
    code, out = _git(repo, "ls-files", "--others", "--exclude-standard")
    if code != 0:
        return None
    untracked = [line for line in out.splitlines() if line.strip()]
    seen = set(staged)
    return ([(rel, "index") for rel in staged]
            + [(rel, "worktree") for rel in untracked if rel not in seen])


def read(repo: Path, rel: str, source: str) -> str | None:
    """The bytes that would be committed.

    For a staged path that is the INDEX, never the working tree: this repo has
    already recorded that a clean tree says nothing about what a commit
    carries.
    """
    if source == "index":
        code, out = _git(repo, "show", ":" + rel)
        return None if code != 0 else out
    try:
        return (repo / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=None,
                        help="the git tree to read (default: this checkout)")
    parser.add_argument("--paths", nargs="*", default=None,
                        help="explicit repo-relative paths instead of the index")
    parser.add_argument("--quiet", action="store_true",
                        help="print only on a refusal or a cannot-answer")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve() if args.repo else SCRIPT_ROOT

    try:
        prop = _load_property()
    except Exception as exc:  # noqa: BLE001 - any import failure means the same thing
        print(f"staged-identity: the property module would not import "
              f"({type(exc).__name__}: {exc}). CANNOT ANSWER -- run "
              f"tests/test_no_committed_identity.py.", file=sys.stderr)
        return CANNOT_ANSWER

    changed = change_set(repo, args.paths)
    if changed is None:
        print("staged-identity: git could not say what changed, so the change "
              "set is UNKNOWN -- not empty. CANNOT ANSWER.", file=sys.stderr)
        return CANNOT_ANSWER

    touched_property = sorted(
        rel for rel, _ in changed if rel in PROPERTY_PATHS)
    if touched_property:
        print("staged-identity: this change edits the property itself (" +
              ", ".join(touched_property) + "), so what counts as a shape or "
              "as a declared plant may have moved. A staged-set answer is no "
              "longer evidence about the files it did not read. CANNOT "
              "ANSWER -- run tests/test_no_committed_identity.py.",
              file=sys.stderr)
        return CANNOT_ANSWER

    hits: list[tuple[str, int, str, str]] = []
    examined = 0
    for rel, source in changed:
        if Path(rel).suffix.lower() in prop.BINARY_SUFFIXES:
            continue
        if prop.HASHY.search(rel):
            continue
        text = read(repo, rel, source)
        if text is None:
            continue
        examined += 1
        found = prop.hits_in(text)
        if not found:
            continue
        counted: dict[str, int] = {}
        for name, _ in found:
            counted[name] = counted.get(name, 0) + 1
        for name, count in sorted(counted.items()):
            allowed = prop.DECLARED_PLANTS.get((rel, name), 0)
            if count <= allowed:
                continue
            for shape, value in found:
                if shape == name:
                    line = _line_of(text, shape, prop)
                    hits.append((rel, line, name, value))

    if hits:
        print("", file=sys.stderr)
        print("REFUSED: a file this commit would write carries an UNDECLARED "
              "identifier shape.", file=sys.stderr)
        print("", file=sys.stderr)
        for rel, line, name, value in hits:
            where = f"{rel}:{line}" if line else rel
            print(f"  {where}  [{name}]  {value}", file=sys.stderr)
        print("", file=sys.stderr)
        print("A SHAPE MATCH MEANS UNDECLARED, NOT REAL. The repair is either "
              "to change the content or to declare the plant in "
              "DECLARED_PLANTS in tests/test_no_committed_identity.py -- and a "
              "declaration permanently widens what the guard tolerates for "
              "that file, so prefer changing the content.", file=sys.stderr)
        print("The value is masked above on purpose; this output reaches "
              "terminals, transcripts and CI logs.", file=sys.stderr)
        return REFUSED

    if not args.quiet:
        if examined == 0:
            # THE LOUD EMPTY. A run that read nothing has said nothing, and
            # printing a bare pass here is how a check that cannot fail gets
            # mistaken for one that did not fire.
            print("staged-identity: examined 0 files. This is a statement "
                  "about the CHANGE SET, not about the tree -- nothing here "
                  "has been checked.", file=sys.stderr)
        else:
            print(f"staged-identity: {examined} file(s) examined, no "
                  f"undeclared shape. The other files in the tree were NOT "
                  f"read; their base case is the whole-tree sweep in CI.",
                  file=sys.stderr)
    return CLEAN


def _line_of(text: str, shape: str, prop) -> int:
    """The first line whose own text still produces this shape. 0 when unknown.

    Per-line rather than per-file because a reviewer needs somewhere to look,
    and 0 rather than a guess when the shape only exists in the whole-file
    context -- the surface may not print a claim it cannot derive.
    """
    for number, line in enumerate(text.splitlines(), start=1):
        for name, _value in prop.hits_in(line, only=shape):
            if name == shape:
                return number
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
