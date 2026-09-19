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

BYPASS, when you genuinely need it: ``git commit --no-verify``. Documented
rather than hidden -- an undocumented bypass gets discovered at the worst
moment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE = "linkedin_server/"
BOUNDARY_TEST = REPO / "tests" / "test_readonly.py"
#: The interpreter the repo's own scripts use. Absent in a bare clone, which is
#: an infrastructure case and therefore a FAIL-OPEN.
PYTHON = REPO / "venv" / "Scripts" / "python.exe"


def staged_package_files() -> list[str]:
    """Package files this commit would write. Reads the INDEX, not the tree."""
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
        if line.strip().startswith(PACKAGE) and line.strip().endswith(".py")
    ]


def main() -> int:
    staged = staged_package_files()
    if not staged:
        # NOT A PASS -- the check did not apply. Silent on purpose: a hook that
        # prints on every unrelated commit trains people to stop reading it.
        return 0

    if not PYTHON.exists():
        print(f"pre-commit[boundary]: {PYTHON.name} not found; ALLOWING. "
              "tests/test_readonly.py still applies -- run it yourself.",
              file=sys.stderr)
        return 0
    if not BOUNDARY_TEST.exists():
        print("pre-commit[boundary]: tests/test_readonly.py is missing; "
              "ALLOWING. That absence is itself worth looking at.",
              file=sys.stderr)
        return 0

    print(f"pre-commit[boundary]: {len(staged)} package file(s) staged; "
          "running the read-only boundary.", file=sys.stderr)
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", str(BOUNDARY_TEST),
         "-q", "-p", "no:randomly", "--tb=line"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode == 0:
        return 0

    # EXIT CODES ABOVE 1 ARE PYTEST FAILING TO RUN -- a collection error, a
    # missing plugin, an internal error. That is infrastructure, not a red
    # boundary, and refusing on it is how a hook earns a bypass habit.
    if proc.returncode not in (1,):
        print(f"pre-commit[boundary]: pytest could not run "
              f"(exit {proc.returncode}); ALLOWING. Output follows.",
              file=sys.stderr)
        print(proc.stdout[-2000:], file=sys.stderr)
        return 0

    print("", file=sys.stderr)
    print("COMMIT REFUSED: the read-only boundary is RED and this commit "
          "touches the package.", file=sys.stderr)
    print("", file=sys.stderr)
    for line in proc.stdout.splitlines():
        if line.startswith("FAILED") or " failed" in line:
            print("    " + line, file=sys.stderr)
    print("", file=sys.stderr)
    print("  staged package files:", file=sys.stderr)
    for name in staged:
        print("    " + name, file=sys.stderr)
    print("", file=sys.stderr)
    print("  This is the project's central safety property. A red boundary at "
          "HEAD makes", file=sys.stderr)
    print("  the read-only claim false in the tree, and code lands on top of "
          "it meanwhile.", file=sys.stderr)
    print("  Run: ./venv/Scripts/python.exe -m pytest tests/test_readonly.py "
          "-q --tb=line", file=sys.stderr)
    print("  Bypass, if you truly mean to: git commit --no-verify",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
