"""Refuse a commit that would leave the READ-ONLY BOUNDARY red at HEAD.

WHY THIS EXISTS, and the receipt is mine.

On 2026-09-19 I committed a new package module at 10:37 having run my own test
file, the navigation taint guard and the identity sweep -- **and not
``tests/test_readonly.py``.** The boundary was red at HEAD for 22 minutes while
more code landed on top of it, and the project's central claim, that this server
is read-only and enforced four ways, was false in the tree for that whole time.

**THE GUARD NEEDED NOTHING. It was not being run.**
``tests/test_readonly.py`` computes ``MODULES = sorted(PACKAGE_DIR.glob("*.py"))``
so it had auto-included the new module the instant the file existed. It was
working perfectly and nobody asked it.

The rule that came out of it is narrower and more useful than "run more tests":

    WHEN YOU ADD A FILE TO ``linkedin_server/``, THE PACKAGE-LEVEL INVARIANTS
    ARE THE TESTS MOST LIKELY TO BE BROKEN BY IT -- AND THEY ARE THE ONES TO
    RUN, NOT THE FILE YOU JUST WROTE.

That is a discipline, and this hook is the same rule as a MECHANISM, at the one
instant that matters: the moment a blob is about to be written. It is the
identity gate's argument applied to a different invariant, and the identity
gate's posture is copied wholesale rather than reinvented.

WHAT IT CHECKS, AND WHEN IT DOES NOT RUN AT ALL.

It runs ``tests/test_readonly.py`` **only when a ``linkedin_server/*.py`` file
is STAGED.** That test is ~7 seconds over ~247 tests, which is fine
occasionally and intolerable on every commit -- and **a slow hook gets
``--no-verify`` habitually, which puts that habit in place on the day it
matters.** A census edit, an audit document or a test-only change does not
touch the package and does not pay for the check.

It reads the INDEX, not the working tree, for the same reason the identity gate
does: the thing being judged is what this commit would write, and in a tree
with several concurrent writers the working tree is a different object.

**IT DOES NOT RUN THE WHOLE SUITE.** A pre-commit hook that runs 5000 tests is
a hook nobody keeps.

FAIL-OPEN ON INFRASTRUCTURE, FAIL-CLOSED ON A REAL RED.

If the interpreter is missing, pytest is absent, the test file is gone, or the
run cannot start, this hook **ALLOWS** and says so on stderr. Only an actual
test failure refuses. That posture is deliberate and it is why the identity
gate is still installed: refusing every commit in a checkout that legitimately
lacks a tool would train everybody to bypass, and the bypass habit is the real
loss. **A hook that is bypassed is worse than no hook, because its presence
implies a check nobody is running.**

WHAT IT CANNOT DO, said here so nobody mistakes it for more.

``.git/hooks/`` is **per-checkout and untracked**. This protects this working
copy and nothing else -- not a clone, not CI, not a teammate's tree. The
identity gate has exactly the same limit. The repo-wide guarantee is the test
itself; this only makes forgetting to run it harder here.

INSTALL -- ONE HOOK, TWO CHECKS. ``.git/hooks/pre-commit`` is a SINGLE FILE, so
a second hook file does not coexist with the first: it replaces it, and the
failure mode is that the identity gate silently stops running. The installed
hook must therefore call both, and **must not use ``exec`` for the first one**,
because ``exec`` replaces the shell and anything after it never runs::

    #!/bin/sh
    ./venv/Scripts/python.exe scripts/pre_commit_identity_gate.py || exit 1
    ./venv/Scripts/python.exe scripts/pre_commit_boundary_gate.py || exit 1

``scripts/install_git_hooks.py`` writes exactly that and is idempotent.

AND THE SAME ARGUMENT, APPLIED TO ``tests/`` -- ADDED 2026-09-19.

The hook above was built because I reported a tree having run only what I
edited. **It then happened again four hours later, and this hook did not fire
either time, because both instances were ``tests/``.**

    morning  changed a shared structure, ran tests/test_readonly.py's subject,
             reported the tree; the boundary was red for 22 minutes
    12:15    changed ``_SANITISERS``, ran the file being edited, reported the
             tree; a DIFFERENT test file's pin had gone red

    A GUARD SCOPED TO WHERE YOU EXPECTED THE DEFECT IS NOT SCOPED TO WHERE
    THE DEFECT IS.

So a staged ``tests/*.py`` now runs the staged file **plus every test file
COUPLED to it**, and the coupling is COMPUTED rather than listed. A hand-written
pair -- the two files that collided today -- would be the same mistake in a new
place: correct for the instance that produced it and blind to the next one.

**THE COUPLING RULE:** file B is coupled to staged file A when B names a
module-level CONSTANT that A defines. That is the shape of both of today's
misses and of the whole class: a shared structure lives in one file and is
pinned in another, so editing the structure moves an assertion the editor never
opened. Whole-word matching, so ``MY_SANITISERS`` does not match
``_SANITISERS``.

It is deliberately NOT an import graph. These files pin each other by NAME --
the taint engine matches a sanitiser by its name corpus-wide, and the second pin
on ``_SANITISERS`` is a literal copy of the set, not an import. An import graph
would see neither.

**WHAT THIS STILL CANNOT SEE:** a coupling carried by a string, a glob, or a
structure whose name B never spells. Those exist, and the honest claim for this
hook is the narrow one -- it catches the constant-sharing class, which is the
class with two receipts, and it makes no claim beyond it.

BYPASS, when you genuinely need it: ``git commit --no-verify``. Documented
rather than hidden -- an undocumented bypass gets discovered at the worst
moment.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE = "linkedin_server/"
TESTS = "tests/"
#: Above this many coupled files the hook is slow enough to get bypassed.
#: It still runs ALL of them -- silently narrowing is the defect this file
#: exists to stop -- and says so, because the repair is a narrower shared
#: structure, not a narrower check.
COUPLING_NOISY_AT = 12
BOUNDARY_TEST = REPO / "tests" / "test_readonly.py"
#: The interpreter the repo's own scripts use. Absent in a bare clone, which is
#: an infrastructure case and therefore a FAIL-OPEN.
PYTHON = REPO / "venv" / "Scripts" / "python.exe"


def staged_paths() -> list[str]:
    """Python files this commit would write. Reads the INDEX, not the tree."""
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode != 0:
        # Infrastructure: git itself failed. Say so and allow.
        print("pre-commit[boundary]: git diff --cached failed; ALLOWING.",
              file=sys.stderr)
        return []
    return [
        line.strip() for line in proc.stdout.splitlines()
        if line.strip().endswith(".py")
    ]


def shared_names(path: Path) -> set[str]:
    """Module-level CONSTANT names defined in a file, off the AST.

    Parsed rather than grepped: an assignment inside a function or a string
    that happens to contain the name is not a definition, and a regex cannot
    tell the difference. Unparseable or unreadable returns EMPTY -- this
    function's failure must never refuse a commit.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return set()
    names: set[str] = set()
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        for target in targets:
            # ``_SANITISERS``.isupper() is True -- underscores are uncased.
            if isinstance(target, ast.Name) and target.id.isupper():
                if len(target.id) > 3:
                    names.add(target.id)
    return names


def coupled_test_files(staged: list[str]) -> list[str]:
    """Test files that NAME a module-level constant a staged test defines.

    This is the mechanism, and its whole claim is in the sentence above: the
    structure lives in one file and is pinned in another, so editing it moves
    an assertion the editor never opened. Twice in one day.
    """
    wanted: set[str] = set()
    for rel in staged:
        wanted |= shared_names(REPO / rel)
    if not wanted:
        return []

    # A NAME DEFINED IN MORE THAN ONE TEST FILE IS A CONVENTION, NOT A SHARED
    # STRUCTURE. ``REPO`` and ``SCANNED`` are declared at the top of dozens of
    # files here; coupling on them drags 31 files in on a single edit, and a
    # hook that runs the tree is a hook that gets bypassed. Measured: the
    # filter costs 0.64s over 157 files and takes the same edit from 31 files
    # to 1 -- the one that actually pins the structure.
    #
    # It is a SUBTRACTION rather than a list of names to ignore, so a
    # convention invented tomorrow is handled without editing this file.
    elsewhere: set[str] = set()
    for path in sorted((REPO / "tests").glob("*.py")):
        if TESTS + path.name in staged:
            continue
        elsewhere |= shared_names(path)
    wanted -= elsewhere
    if not wanted:
        return []

    pattern = re.compile(
        r"\b(" + "|".join(re.escape(n) for n in sorted(wanted)) + r")\b"
    )
    out: list[str] = []
    for path in sorted((REPO / "tests").glob("*.py")):
        rel = TESTS + path.name
        if rel in staged:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if pattern.search(text):
            out.append(rel)
    return out


def main() -> int:
    staged = staged_paths()
    package = [name for name in staged if name.startswith(PACKAGE)]
    tests = [name for name in staged if name.startswith(TESTS)]
    if not package and not tests:
        # NOT A PASS -- the check did not apply. Silent on purpose: a hook that
        # prints on every unrelated commit trains people to stop reading it.
        return 0

    if not PYTHON.exists():
        print(f"pre-commit[boundary]: {PYTHON.name} not found; ALLOWING. "
              "The guards still apply -- run them yourself.",
              file=sys.stderr)
        return 0

    targets: list[str] = []
    reasons: list[str] = []

    if package:
        if BOUNDARY_TEST.exists():
            targets.append("tests/test_readonly.py")
            reasons.append(
                f"{len(package)} package file(s) staged "
                "-> the read-only boundary"
            )
        else:
            print("pre-commit[boundary]: tests/test_readonly.py is missing; "
                  "not running it. That absence is itself worth looking at.",
                  file=sys.stderr)

    if tests:
        coupled = coupled_test_files(tests)
        targets.extend(tests)
        targets.extend(coupled)
        reasons.append(
            f"{len(tests)} test file(s) staged -> themselves "
            f"+ {len(coupled)} coupled by a shared constant"
        )
        if len(coupled) > COUPLING_NOISY_AT:
            print(f"pre-commit[boundary]: {len(coupled)} coupled files. "
                  "Running all of them. If this is slow, narrow the SHARED "
                  "STRUCTURE -- narrowing the check is the defect this hook "
                  "exists to stop.", file=sys.stderr)

    # Dedupe, order preserved, and drop anything that has since vanished: a
    # staged DELETION is filtered out upstream, but a rename race is not.
    seen: set[str] = set()
    plan = [name for name in targets
            if (REPO / name).exists() and not (name in seen or seen.add(name))]
    if not plan:
        return 0

    for reason in reasons:
        print(f"pre-commit[boundary]: {reason}", file=sys.stderr)
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", *[str(REPO / name) for name in plan],
         "-q", "-p", "no:randomly", "--tb=line"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode == 0:
        return 0

    # EXIT CODES ABOVE 1 ARE PYTEST FAILING TO RUN -- a collection error, a
    # missing plugin, an internal error. That is infrastructure, not a red
    # guard, and refusing on it is how a hook earns a bypass habit.
    if proc.returncode not in (1,):
        print(f"pre-commit[boundary]: pytest could not run "
              f"(exit {proc.returncode}); ALLOWING. Output follows.",
              file=sys.stderr)
        print(proc.stdout[-2000:], file=sys.stderr)
        return 0

    print("", file=sys.stderr)
    print("COMMIT REFUSED: a guard over what this commit touches is RED.",
          file=sys.stderr)
    print("", file=sys.stderr)
    for line in proc.stdout.splitlines():
        if line.startswith("FAILED") or " failed" in line:
            print("    " + line, file=sys.stderr)
    print("", file=sys.stderr)
    print("  staged:", file=sys.stderr)
    for name in package + tests:
        print("    " + name, file=sys.stderr)
    print("  ran:", file=sys.stderr)
    for name in plan:
        print("    " + name, file=sys.stderr)
    print("", file=sys.stderr)
    print("  A file NOT in the staged list means a shared structure moved an "
          "assertion", file=sys.stderr)
    print("  somewhere you did not open. That is the whole reason this runs "
          "more than", file=sys.stderr)
    print("  what you edited.", file=sys.stderr)
    print("  Bypass, if you truly mean to: git commit --no-verify",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
